from django.apps import AppConfig
from django.conf import settings
import os


class VirussConfig(AppConfig):
   path = os.path.join(settings.MODELS,'models.p')
   name = 'viruss'
