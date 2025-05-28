import os
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apps.batch import insert_past_schedules

class Command(BaseCommand):
    help = 'Run APScheduler using BlockingScheduler'

    def handle(self, *args, **kwargs):
        batch_enabled = os.getenv("BATCH_ENABLED", "false").lower() == "true"

        if not batch_enabled:
            self.stdout.write('[INFO] BATCH_ENABLED is not true. Skipping scheduler.')
            return

        scheduler = BlockingScheduler()
        scheduler.add_job(insert_past_schedules, 'cron', hour=0, minute=0)
        self.stdout.write('Scheduler started.')
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write('Scheduler stopped.')
