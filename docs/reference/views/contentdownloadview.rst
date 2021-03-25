===================
ContentDownloadView
===================

The ContentDownloadView requires django-weasyprint_ to be installed.

As the ContentEditView and the ContentDeleteView this view works in a parent-child
relation, meaning a downloadpage needs to have a ContentView with the same transfer_model
as parent.

Now that the basics are out of the way, what does this view do?
| This view allows you to easily serve all you objects in as pdf-files.
You do still have to create the necessary templates and css but as with the ContentView
you can split the work by creating a detail template for each modeltype and a
frame template per app and with selecting a template, extending the frame and including
the detail template per object, you are on the fast lane to printing you whole database ;)

Little joke aside, template structure is essentially the same, as for a ContenView.
The reason for separate pdf-templates is mainly that, even though weasyprint does
a good job of rendering templates to pdf, the dimensions and the spacing a often
a bit off when rendering desktop templates. The folder structure here should look
the following::

  app_name/
    templates/
      pdf/
        model_name.html
      app_name/
        pdf/
          frame.html
          sample_pdf_template.html # THIS IS WHAT YOU WOULD CHOOSE ON THE PAGE CREATION


Functions
=========

**dispatch() & get_permission_required()**
  See ContentView. Did not change.

**get_success_url(self)**
  Returns where the user should be redirected to after a successful post-request.

**get(self, request, \*args, \*\*kwargs)**
  Checks if weasyprint was successfully imported. Rest as usual.

**get_object(self, queryset=None)**
  Does all the usual stuff like the ContentView. As it is pointless to have an
  downloadpage without and transfer_model it is required here instead of checking for it.

**get_context_data(self, \*\*kwargs)**
  The tmp_queryset is used for checking if the private-object feature has been
  activated on the model. After that the :code:`context['object_list']` is filled with a
  queryset with at least one object. Then the verbose name of the model is added
  for convenience under :code:`context['model']` and if existing the frame and
  detail template will be added like in the ContentView.

**get_queryset(self)**
  Filters for the parent node, as there will probably be more than on downloadpage.
