===============
ContentEditView
===============

This views focus is on extending the UpdateView to the scope the app is working
on. So as long as you supply the necessary templates and create an page called Editor
as a child node to a normal ContentView with a the same transfer_model on both of them.
You will automatically have an page which will handle creating and updating objects
of this type with all permission capabilities supplied by django-sitetree.

The view also allows you to write a custom form validation on a per model basis.
To make use of this feature simply add a :code:`validate` function to your model::

  def validate(self, *args, **kwargs):
    # in here you have access to
    # the request -> kwargs['request']
    # the form -> kwargs['form']
    # and the error dict -> kwargs['errors']

DO NOT raise errors in this function!! instead use::

  kwargs['form'].add_error(field, ValidationError(msg_string, code=type_string))

This version of error handling should be preferred as it not only allows for finding
all validation errors at the same time, but it also will return the form to the user
with the errors. Then you can highlight incorrect fields and display your error messages
to the user.
| For a more detailed info on how to use custom validation take a look into the DjangoWiki_


.. _DjangoWiki: https://docs.djangoproject.com/en/dev/ref/forms/validation/

Functions
=========

**dispatch() & get_permission_required()**
  See ContentView. Did not change.

**get_success_url(self)**
  Returns where the user should be redirected to after a successful post-request.

**get_object(self, queryset=None)**
  Does all the usual stuff like the ContentView. As it is pointless to have an editor
  without and transfer_model it is required here instead of checking for it.

**get_queryset(self)**
  Filters for the parent node, as there will probably be more than on editor.

**get_form_kwargs(self)**
  When this function gets called, the get_object funcion has already been called,
  but the get_context_data function not. Based on this we do a little switcheroo.
  We initials the form_kwargs with a call to the super function of get_form_kwargs.
  At this stage the reference object for the call is self.object and that still
  contains the site object. After the initialisation we override the instance in
  the form_kwargs with either a new transfer_model instance *(CREATE-STATE)* or
  fetch an existing one *(UPDATE-STATE)*. Remember that as get_object has been
  executed self.model already contains the transfer_model and no longer the Site model.

**get_form_class(self)**
  This function generates a modelform based on the given transfer_model.

  For now it also replaces all M2M-Relation fields with the admin page M2M-widget.

**get_context_data(self, \*\*kwargs)**
  The context is only extended by the default values listed with the ContentView.
  All functionality from the UpdateView can be used.

**post(self, request, \*args, \*\*kwargs)**
  This function sets self.object to the edited object if in *(UPDATE-STATE)* otherwise
  it sets self.object to None *(CREATE-STATE)*.
  After this it will call the validate function of the model if it has been implemented.
  Then it will execute a flattened form.is_valid() call resulting in a return to
  form_valid or form_invalid.

**form_valid(self, form)**
  This function will start by bleaching all TextFields and if the private-objects
  feature has been integrated it will also set the private state of the model.
  It ends returning the super call on its form_valid, executing the default UpdateView
  code.
