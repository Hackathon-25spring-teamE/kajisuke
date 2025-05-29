import os
import logging
from django.core.management.base import BaseCommand
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apps.batch import insert_past_schedules

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run APScheduler using BlockingScheduler'

    def handle(self, *args, **kwargs):
        batch_enabled = os.getenv("BATCH_ENABLED", "false").lower() == "true"

        if not batch_enabled:
            logger.info("[Batch Scheduler] Skipped: BATCH_ENABLED is not true.")
            return

        def batch_wrapper():
            try:
                logger.info("[Batch Job] Starting schedule archiving batch.")
                insert_past_schedules()
                logger.info("[Batch Job] SUCCESS: insert_past_schedules completed.")
            except Exception as e:
                logger.exception("[Batch Job] Exception occurred during schedule archiving: %s", str(e))

        scheduler = BlockingScheduler()
        scheduler.add_job(
            batch_wrapper,
            CronTrigger(hour=0, minute=0),
            id="insert_past_schedules",
            name="Daily Schedule Archiver",
            replace_existing=True,
        )
        
        logger.info("[Batch Scheduler] Scheduler started.")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("[Batch Scheduler] Scheduler stopped by system signal.")
        except Exception as e:
            logger.exception("[Batch Scheduler] Unexpected exception: %s", str(e))
            scheduler.shutdown()
