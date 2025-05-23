from django.apps import AppConfig


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    # ap_scheduler起動処理を追加
    def ready(self):
        from .batch import start
        start()
