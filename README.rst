========
Overview
========

A django application, which implements a flexible and generic viewsystem providing a convenient way to handle
staticpages, model based pages and much more.

SO big question: What exactly does it for you?

TLDR:
=====

dynamic_sites in its core is a combination of a site model representing each page
and a set of generic views which in conjunction with django-sitetree create a powerful
and yet simple system to create and manage static pages and model dependent/displaying pages.

Long Answer:
============

The core of the app is twofold.
On the one side you have the site model of which the instances represent each page
on your website. For each instance you can specify where in your sitetree it is placed
which name it should have (for each language of your website), which template you
you want to be displayed, if so which picture should be displayed in the background,
which rights are needed to access this page and a couple other things.
Most importantly, if wished for, which model instances of the models you registered
to the collecting signal (more on this in the usage part) you would like to be displayed
or edited, printed and so one, on this page. All of this is handled via the admin
interface without any active coding on your site.
Now to the second part. How does all this fancy stuff work so easy.
The core functionality comes from a small number of generic views. Detailed description
of each view are found in the respective chapter. These views serve the not only
the site object you accessed via the url, but also serve the specified model and
the necessary templates to handle it. Depending on the title you gave the site on its creation
it can also handle creation, editing, print-to-pdf, or deletion of objects from the given model.

The core point is here you have a ton of basic functionality for each of your custom
models independent of which fields, capabilities or complexity it has. In addition
you can still add custom pages with your own views as long as you specify the url
pattern above the dynamic_sites.urls include (more in Installation and Usage).

The full Documentation can be found here_

.. _here: https://django-dynamic-sites.readthedocs.io/

* Free software: MIT license



Needed Dependencies
===================

| The package is based on the django-sitetree_ package which handles the tree structure, access permissions and menu generation.
| For the translation capabilities django-modeltranslation_ is used.
| django-bleach_ is used for cleaning textfields.

.. _django-sitetree: https://pypi.org/project/django-sitetree/
.. _django-modeltranslation: https://pypi.org/project/django-modeltranslation/
.. _django-bleach: https://pypi.org/project/django-bleach/

Optional Dependencies
=====================

django-weasyprint_ for printing to pdf via the ContentDownloadView.

.. _django-weasyprint: https://pypi.org/project/django-weasyprint/
