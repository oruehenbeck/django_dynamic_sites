
# this import is copied from django/views/generic/edit.py
from django.forms import models as model_forms

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import ManyToManyField
from django.views.generic import View, DetailView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect
from django.http import Http404
from django.apps import apps

from django_weasyprint import WeasyTemplateView

import re

from .models import Site
from .functions import generate_filterform_class


class RedirectView(View):
    def get(self, request, *args, **kwargs):
        return redirect('content_view', slug=Site.objects.order_by('sort_order').first().slug)


class ContentView(PermissionRequiredMixin, DetailView):
    model = Site
    template_name = ''

    ## HANDELING PERMISSIONS

    # Check if login is required
    def dispatch(self, request, *args, **kwargs):
        obj = super(ContentView, self).get_object()
        if obj.access_loggedin and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # Get required permissions from site
    def get_permission_required(self):
        perms = []
        obj = super(ContentView, self).get_object()
        for perm in obj.access_permissions.all():
            perms.append(perm.content_type.app_label + '.' + perm.codename)
        return perms

    def get(self, request, *args, **kwargs):
        # checking if an empty editor(create new case) has been opened
        if 'editor' in self.kwargs['slug']:
            # if so, redirect to editor_view with id=0
            return redirect('editor_view', rest_url=self.kwargs['rest_url'], slug=self.kwargs['slug'], id=0, page=1)

        # checking if an empty delete has been opened
        if 'delete' in self.kwargs['slug']:
            raise NotImplementedError('Solution for Menulink to Delete without id needed')

        # This is the download all button
        if 'download' in self.kwargs['slug']:
            # redirect to download view with id=0
            return redirect('download_view', rest_url=self.kwargs['rest_url'], slug=self.kwargs['slug'], id=0)

        return super(ContentView, self).get(request, args, kwargs)

    def get_object(self, queryset=None):
        obj = super(ContentView, self).get_object(queryset)
        # checking for cross access
        if obj.url != self.request.path_info:
            raise Http404
        # retrieving and setting the site template
        self.template_name = obj.template.template_path
        if obj.transfer_model:
            self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
            self.app_name = obj.transfer_model.app_label
            filterform_class = generate_filterform_class(self.model)
            self.form = filterform_class()
        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentView, self).get_context_data()
        # adding the chosen bg picture
        context['bg_pic'] = self.object.bg_pic

        # adding genereal information to context
        context['current_path'] = self.request.path[1:]

        # adding transfer_model specific data to the context
        if self.object.transfer_model:
            # checking filter is enabled on the model
            if hasattr(self.model, 'get_filtered'):
                context['object_list'] = self.model.get_filtered(self.request.GET)
            else:
                context['object_list'] = self.model.objects.all()

            context['detail'] = "detail/" + self.model._meta.model_name + ".html"
            context['filter'] = "filter/" + self.model._meta.model_name + ".html"
            context['frame'] = self.app_name + '/page/frame.html'
            context['form'] = self.form
        return context

    def get_queryset(self):
        if self.kwargs['slug'] == 'editor' or self.kwargs['slug'] == 'download':
            parts = self.request.path.split('/')
            parent_slug = parts[-3]
            return self.model.objects.filter(parent__slug=parent_slug)
        return self.model.objects.all()


class ContentEditView(PermissionRequiredMixin, UpdateView):
    model = Site
    fields = '__all__'

    ## HANDELING PERMISSIONS

    # Check if login is required
    def dispatch(self, request, *args, **kwargs):
        obj = super(ContentEditView, self).get_object()
        if obj.access_loggedin and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # Get required permissions from site
    def get_permission_required(self):
        perms = []
        obj = super(ContentEditView, self).get_object()
        for perm in obj.access_permissions.all():
            perms.append(perm.content_type.app_label + '.' + perm.codename)
        return perms

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        obj = super(ContentEditView, self).get_object(queryset)
        # checking for cross access
        check_path = re.sub('\d+\/', '', self.request.path_info)
        if obj.url != check_path:
            raise Http404
        # resetting self.model to the transfer_model so that the default modelform can be used
        # the site can still be found in the context['site']
        self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
        self.app_name = obj.transfer_model.app_label

        # setting which formpage will be shown
        self.template_name = obj.template.template_path[:-5] + '_' + self.kwargs['page'] + '.html'

        return obj

    def get_queryset(self):
        parts = self.request.path.split('/')
        parent_slug = parts[-5]
        return self.model.objects.filter(parent__slug=parent_slug)

    def get_form_kwargs(self):
        """
        changing instance from site to transfer_model object
        NOTE: get_object has already been executed but get_context_data not.
        """
        form_kwargs = super(ContentEditView, self).get_form_kwargs()

        # checking if create(id=0) or edit mode !! in kwargs id is a string !!
        if self.kwargs['id'] == '0':
            form_kwargs['instance'] = self.model()
            return form_kwargs

        # edit case
        form_kwargs['instance'] = self.model.objects.get(pk=self.kwargs['id'])

        return form_kwargs

    def get_form_class(self):
        """
        The Goal of this function extension is to change the
        widgets of all m2m fields to filter_horizontal or
        more accurately FilteredSelectMultiple
        """
        # check if a special page has been called
        if 'get_form_pages' in dir(self.model):
            fields = []
            # getting all pages of the model
            self.pages = self.model.get_form_pages()
            for name in self.pages[self.kwargs['page']]:
                fields.append(self.model._meta.get_field(name))

        else:
            fields = self.model._meta._get_fields()
            self.pages = {'1': '__all__'}

        widgets = {}
        field_names = []
        # 1. Thing to do is to iterate over all fields the form will have
        for field in fields:
            # 2. within the loop, find each m2m field and set
            if isinstance(field, ManyToManyField):
                pass
                #widgets[field.name] = FilteredSelectMultiple(field.verbose_name, is_stacked=False)
            field_names.append(field.name)

        if len(self.pages) == 1:
            field_names = self.pages['1']

        # 3. creating and returning the form
        return model_forms.modelform_factory(self.model, fields=field_names, widgets=widgets)

    def get_context_data(self, **kwargs):
        context = super(ContentEditView, self).get_context_data(**kwargs)

        # adding the chosen bg picture
        context['bg_pic'] = self.object.bg_pic

        # adding general information to context
        context['current_path'] = re.sub('\d+\/', '', self.request.path[1:])[:-7]
        context['prev_page'] = int(self.kwargs['page']) - 1
        context['current_page'] = self.kwargs['page']
        context['next_page'] = int(self.kwargs['page']) + 1

        # adding the app frame which is to be extended from
        context['frame'] = self.app_name + '/page/frame.html'

        # adding the pages if they exist
        if self.pages:
            context['pages'] = self.pages.keys()

        return context

    def post(self, request, *args, **kwargs):
        """
        Overriding Post to integrate create and update functionality
        and custom generic form validation
        """

        obj = self.get_object()

        form = self.get_form()

        if not form.instance.id:
            self.object = None
        else:
            self.object = self.model.objects.get(pk=form.instance.id)

        ## Manually executing form.is_valid() to inject custom form validation
        ## on a generic model independent way

        # the call to form.errors is nessecary to fill up cleaned_data so that it can be accessed
        # in the validate function
        # does custom validation and adds errors to the form
        form.instance.validate(request=self.request, form=form, errors=form.errors)

        if form.is_bound and not form.errors:
            self.object = obj
            return self.form_valid(form)
        else:
            self.object = obj
            return self.form_invalid(form)


class ContentDeleteView(PermissionRequiredMixin, DeleteView):
    model = Site

    # permission_required = ''

    # def get_permission_required(self):
    # obj = super(ContentDeleteView, self).get_object()
    # perms = obj.access_permissions.all()
    # return perms

    def get_success_url(self):
        return '../..'

    def get_object(self, queryset=None):
        obj = super(ContentDeleteView, self).get_object(queryset)
        # checking for cross access
        check_path = re.sub('\d+\/', '', self.request.path_info)
        if obj.url != check_path:
            raise Http404
        # setting background and template
        self.template_name = obj.template.template_path
        self.bg_pic = obj.bg_pic

        # resetting self.model to the transfer_model so that the default modelform can be used
        # the site can still be found in the context['site']
        self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
        self.app_name = obj.transfer_model.app_label
        obj = self.model.objects.get(pk=self.kwargs['id'])

        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentDeleteView, self).get_context_data(**kwargs)

        # adding the chosen bg picture
        context['bg_pic'] = self.bg_pic

        # adding genereal information to context
        context['current_path'] = self.request.path[1:]

        # adding the app frame which is to be extended from
        context['frame'] = self.app_name + '/frame.html'

        return context

    def get_queryset(self):
        return self.model.objects.all()


class ContentDownloadView(PermissionRequiredMixin, SingleObjectMixin, WeasyTemplateView):
    model = Site
    permission_required = ''

    ## HANDELING PERMISSIONS

    # Check if login is required
    def dispatch(self, request, *args, **kwargs):
        self.object = super(ContentDownloadView, self).get_object()
        if self.object.access_loggedin and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # Get required permissions from site
    def get_permission_required(self):
        perms = []
        path_parts = self.request.path.split('/')[:3]
        path_parts.append('')
        site_path = '/'.join(path_parts)
        for perm in self.model.objects.get(url=site_path).access_permissions.all():
            perms.append(perm.content_type.app_label + '.' + perm.codename)
        return perms

    ## HANDELING REQUEST

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ContentDownloadView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return '..'

    def get_object(self, queryset=None):
        obj = super(ContentDownloadView, self).get_object(queryset)
        # checking for cross access
        check_path = re.sub('\d+\/', '', self.request.path_info)
        if obj.url != check_path:
            raise Http404
        # resetting self.model to the transfer_model so that the default modelform can be used
        # the site can still be found in the context['site']
        self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
        self.app_name = obj.transfer_model.app_label
        self.template_name = obj.template.template_path

        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentDownloadView, self).get_context_data()
        if self.kwargs['id'] == '0':
            context['object_list'] = self.model.objects.all()
        else:
            context['object_list'] = self.model.objects.filter(pk=self.kwargs['id'])
            
        context['model'] = self.model._meta.verbose_name
        # adding the app frame which is to be extended from
        context['frame'] = self.app_name + '/pdf/frame.html'
        context['detail'] = "pdf/" + self.model._meta.model_name + ".html"

        return context

    def get_queryset(self):
        parts = self.request.path.split('/')
        parent_slug = parts[-4]
        return self.model.objects.filter(parent__slug=parent_slug)
