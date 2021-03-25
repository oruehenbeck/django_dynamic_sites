===============
Private Objects
===============

This feature allows you now to enable your users to have their own objects of a
model. There are a couple of steps you have to take to use this feature.

| For sake of brevity we assume the following state:

  - You have a project with dynamic_sites integrated and working.
  - You have at least one model hooked up as possible transfer_model.
  - You have created the necessary templates for your sites and model to be
    correctly displayed and edited.

If you are having problems with any of the before mentioned steps, consult the
rest of the documentation and if needed contact me.


Step 1:
=======
Add a boolean Field to your model named :code:`private`.


Step 2:
=======
Create an additional Manager for your model containing a :code:`get_private()`
and a :code:`get_public()` function. Here is an example::

  def get_private(self, *args, **kwargs):
    return super(Private_Objects_Manager, self).get_queryset().filter(creator=kwargs['user'], private=True)

  def get_public(self, *args, **kwargs):
    return super(Private_Objects_Manager, self).get_queryset().filter(private=False)

For your convenience :code:`get_private()` will always have :code:`kwargs['user']`
filled with :code:`self.request.user` from the view calling the manager.


Step 3:
=======
Add your newly created manager to your model as follows::

  class YOURMODEL():
    .
    .
    .

    # Managers

    objects = models.Manager()
    priv_objects = Private_Objects_Manager()

If you did not use any previous custom managers on the model. You will have to add
the regular the line :code:`objects = models.Manager()`:


Step 4:
=======
Create a template for your user page. In the template you can access the current
user with :code:`{{ object }}`.

Step 5:
=======
| In the admin menu:
  - Add the userpage template to your dynamic_sites templates
  - Create a Site in your sitetree with 'user' in the title and your userpage template
    and check the box saying 'logged in only'


DONE!
=====
Thats it! All sites you hook beneath your userpage and that use this model as
transfer_model will automatically only show objects returned by the :code:`get_private()`
manager function and if the sites are not hooked beneath the userpage they will
show all objects returned by :code:`get_public()`.

As you can expect this works for as many models as you register and extend the
shown way.
