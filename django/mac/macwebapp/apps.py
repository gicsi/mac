from django.apps import AppConfig
from material.frontend.apps import ModuleMixin


class MacwebappConfig(ModuleMixin, AppConfig):
    name = 'macwebapp'
    verbose_name = 'MAC'
    icon = '<i class="material-icons">menu</i>'
