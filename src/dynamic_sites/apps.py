from django.apps import AppConfig


class DynamicSitesConfig(AppConfig):
    name = 'dynamic_sites'
    
    def ready(self):
        from dynamic_sites import signals
