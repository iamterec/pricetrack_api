from celery import Celery

celery_app = Celery("beat", broker="pyamqp://rabbitmq:5672")

celery_app.conf.beat_schedule = {
    'get_items': {
        'task': 'tasks.scraping.get_items',
        'schedule': 3600.0,
        'args': ()
    },
}

## alternative way:
# from tasks.scraping import get_items
# @celery_app.on_after_configure.connect
# def setup_periodic_task(sender, **kwargs):
#     # sender.add_periodic_task(10.0, reverse.s(("hello from scheduled",)), name="hello world scheduled task")
#     sender.add_periodic_task(10.0, get_items.s(), name="get_items")
