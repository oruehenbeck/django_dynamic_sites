========
Overview
========

A django application, which implements a flexible and generic viewsystem providing a convinient way to handle
staticpages, model based pages and much more.

* Free software: MIT license

Installation
============

::

    pip install django_dynamic_sites

You can also install the in-development version with::

    pip install git+https://github.com/oruehenbeck/django_dynamic_sites.git@master

Documentation
=============


https://django-dynamic-sites.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
