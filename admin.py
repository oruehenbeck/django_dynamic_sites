# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy

from sitetree.models import Tree
from sitetree.admin import TreeItemAdmin, TreeItemForm, override_item_admin

from modeltranslation.admin import TranslationAdmin

from .models import Template, Site
from .signals import get_transferable_models


class SiteAdminForm(TreeItemForm):
    class Meta:
        model = Site
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        transferable_models = []
        get_transferable_models.send(sender='dynamic_sites', qry=transferable_models)
        qs_transferable_models = ContentType.objects.none()
        for qs in transferable_models:
            qs_transferable_models = qs_transferable_models | qs
        super(SiteAdminForm, self).__init__(*args, **kwargs)
        self.fields['transfer_model'].queryset = qs_transferable_models

    def decendents_update_url(self, _instance):
        """
        :param TreeItem _instance:
        """
        for child in _instance.site_parent.all():
            child.url = child.parent.url + child.slug + '/'
            child.save()
            self.decendents_update_url(child)

    def _post_clean(self):
        super(SiteAdminForm, self)._post_clean()
        """
        The instance does not need to be saved here
        because it will be saved later by the rest of the
        intern admin functions
        """

        if self.instance.pk:
            ### Edit mode ###
            parent_changed = False
            title_changed = False

            # grab old item from db to check what has changed
            old_item = Site.objects.get(pk=self.instance.pk)

            # checking parent_change
            if self.cleaned_data['parent'] != old_item.parent:
                parent_changed = True
                self.instance.parent = self.cleaned_data['parent']

            # checking name change which results in changing the slug
            if self.instance.title != old_item.title:
                self.instance.slug = slugify(self.instance.title)
                title_changed = True

            # updating the url
            if (parent_changed or title_changed) and self.cleaned_data['parent']:
                self.instance.url = self.cleaned_data['parent'].url + self.instance.slug + '/'
            elif parent_changed or title_changed:
                self.instance.url = '/' + self.instance.slug + '/'

            if parent_changed or title_changed:
                self.decendents_update_url(self.instance)

        else:
            # creating slug
            self.instance.slug = slugify(self.instance.title)

            # generating fitting url
            if self.cleaned_data['parent']:
                self.instance.url = self.cleaned_data['parent'].url + self.instance.slug + '/'
            else:
                self.instance.url = '/' + self.instance.slug + '/'

            # setting Tree
            self.instance.tree = Tree.objects.first()


class SiteAdmin(TreeItemAdmin, TranslationAdmin):
    form = SiteAdminForm

    readonly_fields = ['slug', 'url', 'tree']
    exclude = ('sort_order',)
    fieldsets = (
        (pgettext_lazy('Admin page Basic settings', 'DynamicSitesSiteAdmin_0'), {
            'fields': ('parent', 'title', 'display_title', 'title_text', 'template', 'bg_pic', 'transfer_model', 'tree', 'slug', 'url',)
        }),
        (pgettext_lazy('Admin page Access settings', 'DynamicSitesSiteAdmin_1'), {
            'fields': ('access_loggedin', 'access_guest', 'access_restricted', 'access_permissions', 'access_perm_type')
        }),
        (pgettext_lazy('Admin page Display settings', 'DynamicSitesSiteAdmin_2'), {
            'classes': ('collapse',),
            'fields': ('hidden', 'inmenu', 'inbreadcrumbs', 'insitetree')
        }),
        (pgettext_lazy('Admin page Additional settings', 'DynamicSitesSiteAdmin_3'), {
            'classes': ('collapse',),
            'fields': ('hint', 'description', 'alias', 'urlaspattern')
        }),
    )

    filter_horizontal = ('access_permissions',)


admin.site.register(Template)
override_item_admin(SiteAdmin)
