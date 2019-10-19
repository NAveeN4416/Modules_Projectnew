from django.apps import AppConfig


class ProductsConfig(AppConfig):
    name = 'products'
    verbose_name = "Products"

    def ready(self):
    	from .import signals