from celery import Celery

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.secret_settings import EmailSecret

from config.settings import CLIENT_URI

celery_app = Celery("email", broker="pyamqp://rabbitmq:5672")
celery_app.conf.task_routes = {"tasks.email.*": {"queue": "emails"}}

try:
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(EmailSecret.EMAIL_ADRESS, EmailSecret.PASSWORD)
except Exception as e:
    print("Exception raised during email server creation:", e)


def get_change_password_html(link):
    with open("tasks/assets/change_password.html") as file:
        file_str = "".join(file.readlines())
        file_str = file_str.format(link=link)
        # file_str.replace("{{Your_token_here}}", link)
    return file_str


@celery_app.task
def send_reset_link(email: str, token: str):
    try:
        # server = smtplib.SMTP("smtp.gmail.com:587")
        # server.starttls()
        # server.login(EMAIL_ADRESS, PASSWORD)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Pricetrack: change password"
        msg['From'] = EmailSecret.EMAIL_ADRESS
        msg['To'] = email

        # url = UI_URL + "change-password/" + token
        # html = render_html("./tasks/change_password.html", link=url)

        url = CLIENT_URI + "/password-change/" + token
        html = get_change_password_html(url)

        msg.attach(MIMEText(html, "html"))
        server.sendmail(EmailSecret.EMAIL_ADRESS, "iamterec@gmail.com", msg.as_string())
    except Exception as e:
        print("Exception: ", e)

