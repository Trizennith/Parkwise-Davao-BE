from django.apps import AppConfig


class JwtBlacklistConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jwt_blacklist"

    def ready(self):
        import apps.jwt_blacklist.signals  # noqa
