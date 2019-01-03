from celery import Celery

celery_app = Celery("test", broker="pyamqp://rabbitmq:5672")

@celery_app.task
def reverse(text):
    return text[::-1]

@celery_app.task
def repeat_print(text):
    print(text)
    return text
