from django.apps import AppConfig
from django.core.serializers import register_serializer

class PolicyWizardConfig(AppConfig):
    name = 'policy_wizard'

    def ready(self):
        register_serializer('yml', 'django.core.serializers.pyyaml')