
# this import is copied from django/views/generic/edit.py
from django.forms import models as model_forms

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import ManyToManyField, TextField
from django.views.generic import View, DetailView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from django.shortcuts import redirect
from django.http import Http404, HttpResponseRedirect
from django.apps import apps

######################################################################################
# allowing the module to be installed without installing Weasyprint/using the Downloadview
weasyerror=None
try:
    from django_weasyprint import WeasyTemplateView
except Exception as e:
    WeasyTemplateView = View
    weasyerror = e
######################################################################################

import re
import os
import bleach

from .models import Site
# from .functions import generate_filterform_class # kept as reminder see to-do in contentview get_object


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
            return redirect('editor_view', rest_url=self.kwargs['rest_url'], slug=self.kwargs['slug'], id=0)

        # checking if an empty delete has been opened
        if 'delete' in self.kwargs['slug']:
            raise NotImplementedError('Solution for Menulink to Delete without id needed')

        # This is the download all button
        if 'download' in self.kwargs['slug']:
            # redirect to download view with id=0
            return redirect('download_view', rest_url=self.kwargs['rest_url'], slug=self.kwargs['slug'], id=0)
        
        # This is the form/mutliform view
        if 'form' in self.kwargs['slug']:
            # allowing for toplayer forms
            if 'rest_url' not in self.kwargs:
                self.kwargs['rest_url'] = ''
            return redirect('form_view', rest_url=self.kwargs['rest_url'], slug=self.kwargs['slug'])

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
            #filterform_class = generate_filterform_class(self.model) #TODO Recreate functionallity for integrating a filter into the view to increase usability
            #self.form = filterform_class() # example is using one site as a listview and enabling the user to reduce the displayed objects with fitting filtersettings
        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentView, self).get_context_data()
        # adding the chosen bg picture
        context['bg_pic'] = self.object.bg_pic

        # adding genereal information to context
        context['current_path'] = self.request.path[1:]

        # adding title #TODO change to display_title or remove, propably first option
        context['title'] = self.object.url

        # adding transfer_model specific data to the context
        if self.object.transfer_model:
            # checking filter is enabled on the model
            if hasattr(self.model, 'get_filtered'): #Keeping until the filter topic is solved and @ that point it has propably be refittet to work
                context['object_list'] = self.model.get_filtered(self.request.GET)
            else:
                context['object_list'] = self.model.objects.all()

            # assining links to vars, to only have one place where they are specified
            extensions = {}
            extensions['detail'] = "detail/" + self.model._meta.model_name + ".html"
            extensions['filter'] = "filter/" + self.model._meta.model_name + ".html"
            extensions['frame'] = self.app_name + '/page/frame.html'
            # Probing if file exists and if so put it into the context
            for i in extensions:
                try:
                    loader.get_template(extensions[i])
                    context[i] = extensions[i]
                except TemplateDoesNotExist:
                    pass

            #context['form'] = self.form # SEE FORM TO-DO in get_object
        return context

    def get_queryset(self):
        if self.kwargs['slug'] == 'editor' or self.kwargs['slug'] == 'download':
            parts = self.request.path.split('/')
            parent_slug = parts[-3]
            return self.model.objects.filter(parent__slug=parent_slug)
        return self.model.objects.all()


class ContentFormView(PermissionRequiredMixin, SingleObjectMixin, TemplateResponseMixin, View):
    model = Site

    ## HANDELING PERMISSIONS

    # Check if login is required
    def dispatch(self, request, *args, **kwargs):
        obj = super(ContentFormView, self).get_object()
        if obj.access_loggedin and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # Get required permissions from site
    def get_permission_required(self):
        perms = []
        obj = super(ContentFormView, self).get_object()
        for perm in obj.access_permissions.all():
            perms.append(perm.content_type.app_label + '.' + perm.codename)
        return perms

    ## HANDELING REQUEST

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        forms = self.get_forms()

        invalid = False
        for form in forms:
            if not form.is_valid():
                invalid = True
                break

        if invalid:
            # tweaked form_invalid
            return self.render_to_response(self.get_context_data(forms=forms))
        else:
            return self.forms_valid(forms)

    def forms_valid(self, forms):
        # Behavior if multiform is implemented
        if not hasattr(self.model, 'special_form_valid'):
            raise NotImplementedError('Please implement the special_form_valid function on your model.')

        self.model.special_form_valid(forms)
        ## flatten super() call
        """If the form is valid, redirect to the supplied URL."""
        return HttpResponseRedirect(self.get_success_url())

    ## GENERAL STUFF

    def get_success_url(self):
        return ('/' + self.kwargs['rest_url']) if 'rest_url' in self.kwargs.keys() else '/'

    def get_object(self, queryset=None):
        obj = super(ContentFormView, self).get_object(queryset)
        # checking for cross access
        check_path = re.sub('\d+\/', '', self.request.path_info)
        if obj.url != check_path:
            raise Http404
        # resetting self.model to the transfer_model so that the default modelform can be used
        # the site can still be found in the context['site']
        self.template_name = obj.template.template_path
        if obj.transfer_model:
            self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
            self.app_name = obj.transfer_model.app_label
        return obj

    def get_context_data(self, **kwargs):
        context = super(ContentFormView, self).get_context_data(**kwargs)

        # adding the chosen bg picture
        context['bg_pic'] = self.object.bg_pic

        # adding general information to context
        context['current_path'] = re.sub('\d+\/', '', self.request.path[1:])[:-7]

        # adding the app frame which is to be extended from
        context['frame'] = self.app_name + '/frame.html'

        if not 'forms' in context:
            context['forms'] = self.get_forms()

        return context

    # MULTIFORM FUNCTIONS

    def get_initials(self, prefix):
        if hasattr(self.model, 'initials'):
            initials = self.model.initials()
            return initials[prefix]
        else:
            return {}

    def get_forms(self):
        """
        This function gets the intended formclass for the transfermodel
        through the special_form classmethod
        """
        # Multiform mode
        forms = []
        options = self.model.special_form()
        for idx, entry in enumerate(options):
            if isinstance(entry, str):
                # get the right model via contenttypes and then instanciate a create form
                tmp = entry.split('/')
                ct = ContentType.objects.get(app_label=tmp[0].lower(), model=tmp[1].lower())
                model = ct.model_class()

                widgets = {}
                field_names = []
                # 1. Thing to do is to iterate over all fields the form will have
                for field in options[entry]:
                    # !! WATCH OUT SWAPPING FROM STRING TO ACTUAL FIELD HERE !!
                    field = model._meta.get_field(field)
                    # 2. within the loop, find each m2m field and set
                    if isinstance(field, ManyToManyField):
                        widgets[field.name] = FilteredSelectMultiple(field.verbose_name, is_stacked=False)  # TODO CHANGE IF FILTEREDSELECTMULTIPE SHOULD NOT BE DEFAULT, ELSE EXTEND FOR OVERRIDING
                    field_names.append(field.name)

                # 3. creating the form_class
                form_class = model_forms.modelform_factory(model, fields=field_names, widgets=widgets)
                forms.append(form_class(**self.get_specific_form_kwargs(prefix=idx)))
            else:
                # instantiate the given form
                forms.append(entry(**self.get_specific_form_kwargs(prefix=idx)))

        return forms

    def get_specific_form_kwargs(self, prefix):
        """
        Return the keyword arguments for instantiating the form.
        Based on the prefix of the form.
        """
        kwargs = {
            'initial': self.get_initials(prefix=prefix),
            'prefix': prefix,
        }

        if self.request.method in ('POST', 'PUT'):
            # filtering data for the right prefix
            data_dict = {}
            if prefix == 0:
                pattern = '^(\d+-)'
            else:
                pattern = '^(' + str(prefix) + '-)'
            for data in self.request.POST:
                if prefix != 0 and re.match(pattern, data):
                    data_dict[data] = self.request.POST[data]

                if prefix == 0 and not re.match(pattern, data):
                    # skipping csrftoken
                    if data == 'csrfmiddlewaretoken':  # TODO IMPROVE TO ALLOW FOR MORE POSSIBLE TOKENS MAYBE AS A SETTING OR SO
                        continue
                    data_dict[data] = self.request.POST[data]

            kwargs.update({
                'data': data_dict,
                'files': self.request.FILES,  # TODO FILTER FILES IN RESPECT TO THE SPECIFIC FORM PREFIX
            })
        return kwargs


#########################################################################################################
##################### SINGLEOBJECT VIEWS ################################################################
#########################################################################################################


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
        self.template_name = obj.template.template_path

        return obj

    def get_queryset(self):
        parts = self.request.path.split('/')
        parent_slug = parts[-4]
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
        fields = self.model._meta._get_fields()

        widgets = {}
        field_names = []
        # 1. Thing to do is to iterate over all fields the form will have
        for field in fields:
            if not field.editable:
                continue
            # 2. within the loop, find each m2m field and set
            if isinstance(field, ManyToManyField):
                widgets[field.name] = FilteredSelectMultiple(field.verbose_name, is_stacked=False)
            field_names.append(field.name)

        # 3. creating and returning the form
        return model_forms.modelform_factory(self.model, fields=field_names, widgets=widgets)

    def get_context_data(self, **kwargs):
        context = super(ContentEditView, self).get_context_data(**kwargs)

        # adding the chosen bg picture
        context['bg_pic'] = self.object.bg_pic

        # adding general information to context
        context['current_path'] = re.sub('\d+\/', '', self.request.path[1:])[:-7]

        # adding the app frame which is to be extended from
        context['frame'] = self.app_name + '/page/frame.html'

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

    def form_valid(self, form):
        for field in form.instance._meta.fields:
            if not field.name in form.cleaned_data:
                continue
            if isinstance(field, TextField):
                form.cleaned_data[field.name] = bleach.clean(form.cleaned_data[field.name])

        return super(ContentEditView, self).form_valid(form)


class ContentDeleteView(PermissionRequiredMixin, DeleteView):
    model = Site

    ## HANDELING PERMISSIONS

    # Check if login is required
    def dispatch(self, request, *args, **kwargs):
        obj = super(ContentDeleteView, self).get_object()
        if obj.access_loggedin and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    # Get required permissions from site
    def get_permission_required(self):
        perms = []
        obj = super(ContentDeleteView, self).get_object()
        for perm in obj.access_permissions.all():
            perms.append(perm.content_type.app_label + '.' + perm.codename)
        return perms

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
        # if weasyprint wasnt installed error here instead of when server is started
        # allowing for full functionality of the rest if download is not used
        if weasyerror:
            raise weasyerror

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
