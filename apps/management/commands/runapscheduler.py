from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apps.batch import insert_past_schedules

class Command(BaseCommand):
    help = 'Run APScheduler using BlockingScheduler'

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler()
        scheduler.add_job(insert_past_schedules, 'cron', hour=1, minute=7)
        self.stdout.write('Scheduler started.')
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write('Scheduler stopped.')
