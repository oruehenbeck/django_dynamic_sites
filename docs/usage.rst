=====
Usage
=====

The assumed state for this page will be a newly setup project following the
installation tutorial, started the server at least once and that you have taken
a look into the website and the admin menu.
If your integrating dynamic_sites into a existing project i recommend reading
through this chapter anyways, as it will showcase multiple use cases and
functionalities in a clean way.


Add a template
==============

- in the admin menu
- go to Dynamic_Sites/Templates

Templates need a name for your own convenience and a path. The path has to have
the same format as if you would specify a template_name in a view.


Register your model
===================

To be able to choose your models as the transfer_model of a page, you need to
register them to the get_transferable_models Signal::

	from dynamic_sites.signals import get_transferable_models
	from dynamic_sites.functions import ret_contenttypes


	@receiver(get_transferable_models)
	def register_transferable_models(sender, *args, **kwargs):
		kwargs['qry'].append(ret_contenttypes(app_label=__name__.split('.')[0], whitelist=['',])) # can specify whitelist or blacklist of modelnames


Creating a new page
===================

- in the admin menu
- Go to Site Trees
- click on the sitetree named 'root'
- one the right side of the window is a gray button labeled 'ADD SITE TREE ITEM'

Now you can create a new site. On the page before you saw a list of items with one
item named 'Defaultpage'. Thats where you can see you sitetree developing when
you add more pages to your website.

In the editor you can now specify your new page, we will go through the options
one by one.

- *parent*:
	Select under which page you want to hook your new page. Leaving it empty means
	the page is in the to player. Editor, download and delete pages have to be
	hooked below another page having the same transfer_model.

- *title*:
	The title is the logical name of the page, it will be its slug and it used to
	give the page special capabilities. Details to the Views are found in the
	respective chapters. All of specialized views need a transfer_model.

	- Title contains 'form': This page will be a ContentFormView.
	- Title == 'Editor': This page will be a ContentEditView.
	- Title == 'Delete': This page will be a ContentDeleteView.
	- Title == 'Download': This page will be a ContentDownloadView.
	- Everything else will be a normal ContentView.


- *display_title*:
	For each language you specified in your settings, set the name which it will
	be displayed as in the menus.

- *title_text*:
	For each language you specified in your settings, set a short description of
	the page, will be available in the context.

- *template*:
	The template in which the context will be rendered in.

- *bg_pic*:
	Here you can add a picture, if the chosen template supports a background picture
	otherwise it will be ignored. Will be added to the context as bg_pic.

- *transfer_model*:
	The juicy part of this project. Here you can select which of your registered
	models should be handled by the page.

The rest of the options are supplied by the django-sitetree app and are explained in its documentation.
