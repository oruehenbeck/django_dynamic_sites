============
Installation
============

At the command line::

    pip install django_dynamic_sites


Setup & Initialisation on a project **without** previous django-sitetree
========================================================================

Changes in the settings.py:

    1. installed apps::

        'modeltranslations', #<- before contrib.admin
        ....
        'sitetree',
        'dynamic_sites',

    2. specify LANGUAGES, first specified language is the default for modeltranslation, example::

        LANGUAGES = [
            ('de', _('German')),
            ('en', _('English')),
        ]

    3. specify SITETREE_MODEL_TREE_ITEM::

        SITETREE_MODEL_TREE_ITEM = dynamic_sites.Site

Changes in your main urls.py:

    1. include the dynamic_sites urls as the last thing::

        path('', include('dynamic_sites.urls')),

On an new project you can intialise the basic site structures using::

    python manage.py init_dynamic_sites

It creates a sitetree named root and sets up a default page allowing you to
experiment with the app and see how its working.


\[WIP\] Setup & Integration on a project **with** django-sitetree
=================================================================

Tutorial will be added when this case has been tested enough to have generic way
of integration.
For now here a couple of things you have to think about:
    - the site objects are added on a fixed sitetree named root and alias root


If you have questions, contact me and i will see if i can help you with the integration.
