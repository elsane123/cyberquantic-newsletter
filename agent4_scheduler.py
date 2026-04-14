"""
Agent 4 — Scheduler
APScheduler: newsletter lundi 8h UTC + blog mardi/jeudi 9h UTC
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from main import run

logging.basicConfig(level=logging.INFO, format='%(asctime)s [Scheduler] %(message)s')
log = logging.getLogger('scheduler')

def newsletter_job():
    log.info('📬 Weekly newsletter job triggered')
    try:
        result = run('send')
        log.info(f'Newsletter published: {result.newsletter_url}')
    except Exception as e:
        log.error(f'Newsletter job failed: {e}')

def start():
    scheduler = BlockingScheduler(timezone='UTC')
    # Newsletter: every Monday at 08:00 UTC
    scheduler.add_job(newsletter_job, CronTrigger(day_of_week='mon', hour=8, minute=0), id='weekly_newsletter')
    log.info('⏰ Scheduler started — Newsletter: Monday 08:00 UTC')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info('Scheduler stopped')

if __name__ == '__main__':
    start()
