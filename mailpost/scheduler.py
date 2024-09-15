from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import send_mailing


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_mailing, "interval", minutes=1)
    scheduler.start()
