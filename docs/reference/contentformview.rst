===============
ContentFormView
===============

This view might look a bit bloated at first glance, but its not just a simple formview.
Its functionality has been furthered to create and join multiple forms into one.
All that is necessary is that you choose a transfer_model for the page and specify
the three following classmethods on the model.
| *Don't forget to create a template for the page using the form(s) ;)*

  1. special_form(cls)
    This method should return a dict containing all models and or custom forms you
    want to have in the mutliform. The structure should look like the following::

      {
        Customform1: [],
        'app_label/model': ['field1', 'field3', 'field4'],
        Customform3: [],
        'app_label/model': ['field2', 'field4', 'field5'],
      }

    | Note a couple of things here.
    | First the order in which you enter your forms here will be the same for the
      other two classmethods.
    | Second no need for double work, for custom form classes you do not specify
      the fields you want to use. You did that in you forms.py
    | Third for adding models the given string format is mandatory. No spaces and
      don't forget the slash.

  2. initials(cls)
    This method should return a doubled dict containing the initial data for the
    forms. Regarding the structure of the dicts the first note from before comes
    into play. Example::

      {
        0: {'first_name': 'Max', 'last_name': 'Mustermann'}, # Assuming Customform1 has these two fields
        1: {'field1': '123354325', 'field3': 'Pancakes', 'field4': False},
        2: {},
        3: {'field2': 'Water'}
      }

    If you do not need to set any initials than you can choose not to implement
    this function.

  3. special_form_valid(cls, forms)
    This classmethod will be called as regular form_valid for the multiform. So
    you can do here anything you would do in your form_valid like overriding values
    setting values which were not fields in the forms and choosing the order in
    which to save the forms::

      forms[0].save()
      forms[1].save()
      forms[2].save()
      forms[3].instance.field3 = forms[1].instance
      forms[3].save()

    **NOTE**
      that you have to call the save functions as there is nothing to
      call super from or that gets executed afterwards.


Functions
=========

**dispatch() & get_permission_required()**
  See ContentView. Its the same stuff.

**get(self, request, \*args, \*\*kwargs)**
  Short function. It calls get_object and then renders get_context_data in a response.

**post(self, request, \*args, \*\*kwargs)**
  Calls get_object and get_forms, then checks for each form if it is valid. If
  any form is invalid, the view form returns a response containing the input and
  the error messages. If everything is fine forms_valid gets called.

**get_success_url(self)**
  Standard class based view function, Just returns where the View should redirect
  to one a successfully send form. It will redirect one layer up the sitetree.

**get_object(self, queryset=None)**
  See ContentView. Doing the same stuff here.

**get_context_data(self, \*\*kwargs)**
  Returns the same default context as the ContentView. Only difference is that
  you will have all the forms in your context under 'forms'.

**get_initials(self, prefix)**
  Loads the initial form values from the classmethod, if implemented.

**get_forms(self)**
  Loads the options from the special_form classmethod. After that it iterates over
  the given customforms and models and either generates a modelform with the
  specified fields or instantiates the customform. All with a overall unique prefix
  so that every form and field can be properly adressed.

**get_specific_form_kwargs(self, prefix)**
  This function returns the input of the multiform on a per form basis. It uses
  the previous set prefixes to filter through the request data.

  | \[WIP\] to main things that need a better solution. One is the cookie detection
    and the other is the file handling.

**forms_valid(self, forms)**
  This function checks if the special_form_valid has been implemented and if not
  raises a NotImplementedError. Regularly it just calls special_form_valid and then
  redirects to the success_url.
