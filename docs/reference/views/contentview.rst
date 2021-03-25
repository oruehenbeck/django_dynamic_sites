===========
ContentView
===========

| This view handles all pages without the need for special features.
| If you don't set a transfer_model for a page it just serves a fixed
context and the chosen template to the template engine.

The fixed context contains the following informations, for you to use in your
template::

  context = {
    'object': <Site: Defaultpage>,
    'site': <Site: Defaultpage>,
    'view': <dynamic_sites.views.ContentView object at 0x7fd23dae4d60>,
    'bg_pic': None,
    'current_path': 'defaultpage/',
    'title': 'Defaultpage'
  }


Functions
=========

**dispatch() & get_permission_required()**
  These to functions enable the permission settings of django-sitetree. The
  customization allows for the access permissions set in the admin interface to
  be checked and respected.

**get()**
  As the ContentView also gets called on the catchall. The get function has been
  extended to filter/redirect, if for example and editor has been called without
  an id.

**get_object()**
  This function has been extended with two additional functionalities. First it
  tests if the requested url fits to the fetched site object. If successful the
  function writes some settings from the object into the view. These being::

    self.template_name = obj.template.template_path
        if obj.transfer_model:
            self.model = apps.get_model(obj.transfer_model.app_label, obj.transfer_model.model)
            self.app_name = obj.transfer_model.app_label

**get_context_data()**
  The default context has been shown before,so we will focus here on the work
  regarding the transfer_model handling. The function will check if the following
  templates exist and if so will add them to the context. It will also add
  \[WIP\] *all the objects* from the transfer_model to the context as object_list.

   - A detail template @ 'detail/' + transfer_model name + '.html'
   - \[WIP\] A filter template @ 'filter/' + transfer_model name + '.html'
   - A frame template @ app_name + 'page/frame.html'

  The intention here is the following. When using the module to create a side you
  can for example use a simple list template. If the list template now includes
  the detail template for each object in the object_list and extends the frame
  template, you essentially can create pages for each model and app, Which look
  differend per app and model you display.

**get_queryset()**
  There has been a small extension in this function, just regarding the editor
  and download pages, which are mainly defined via their position in the sitetree
  instead of the title. Therefore this function prefilters the sites to prevent
  returning more than one page with the same name.
