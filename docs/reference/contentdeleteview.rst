=================
ContentDeleteView
=================

As with the ContentEditView this view unfolds its magic as long a its a child node
of a ContentView page with the same transfer_model set in both of them.

The deletepages created should always have the the display setting `hidden` on True,
as accessing it without an object id is rather pointless.

In general this view does what the name implies it deletes an object of the set
transfer_model specified by the supplied id. It allows for the template to use a
form for asking back if the delete is intended. Just use something like this in
your template::

  <form class="align-center" method="post" action="">
      {% csrf_token %}
      <p>Are you sure that you want to delete <b>{{ object }}</b>?</p>
      <button type="submit alt" value="submit">Yes, delete it!</button> <button type="submit alt" name="cancel">I changed my mind.</button>
  </form>



Functions
=========

**dispatch() & get_permission_required()**
  See ContentView. Did not change.

**get_success_url(self)**
  Returns where the user should be redirected to after a successful post-request.

**get_object(self, queryset=None)**
  In this view the get_object function needs a bit of our intention as its doing
  some switcheroo to be able to use most of the default DeleteView code.

  The first half of the code is the usual stuff you know from the ContentView.
  The second half is therefore more interesting. As base the DeleteView expects
  the get_object function to return the object which is to be deleted. But we are
  using Site as the model and the deletepage/site object in the super call of get_object.
  Based on this we first set self.model to our transfer_model as usual and then
  generate a temporary queryset, respecting if the private-object feature is activated.
  From the queryset we than get our object to be deleted and return it.

  The rest is handled by the default DeleteView.

**get_context_data(self, \*\*kwargs)**
  The context is only extended by the default values listed with the ContentView.
  All functionality from the DeleteView can be used.

**get_queryset(self)**
  Filters for the parent node, as there will probably be more than on deletepage.
