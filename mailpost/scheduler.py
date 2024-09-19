from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import send_mailing

scheduler = None


def start():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_mailing, "interval", minutes=1)
        scheduler.start()
