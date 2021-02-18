# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from sitetree.models import Tree

from dynamic_sites.models import Site, Template


class Command(BaseCommand):
    help = 'Initialises all necessary objects after the migration of the app.'

    def handle(self, *args, **options):
        # checking sitetree tree
        try:
            tree = Tree.objects.all()
        except:
            tree = Tree.objects.none()
            
        if tree.exists():
            self.stderr("It seems like you are integrating this app into a project with an existing sitetree. Please do the integration manually with regards to your project.")
        
        tree = Tree(title='root', alias='root')
        tree.save()
        # creating default page
        template = Template(name='Default', template_path='dynamic_sites/default.html')
        template.save()
        site = Site(title='Defaultpage', title_text='Here you can add some subtitle or something similar.', template=template, tree=tree, access_loggedin=True, url='/defaultpage/', slug='defaultpage')
        site.save()
