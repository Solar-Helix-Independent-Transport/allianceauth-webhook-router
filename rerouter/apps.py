from django.apps import AppConfig
from . import __version__


class PingerConfig(AppConfig):
    name = 'rerouter'
    label = 'rerouter'

    verbose_name = f"Webhook Re-Router v{__version__}"
