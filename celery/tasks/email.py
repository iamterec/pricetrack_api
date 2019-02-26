import smtplib
from celery import Celery
from config.secret_settings import EmailSecret
from config.settings import CLIENT_URI
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException, SMTPAuthenticationError


celery_app = Celery("email", broker="pyamqp://rabbitmq:5672")
celery_app.conf.task_routes = {"tasks.email.*": {"queue": "emails"}}


def get_change_password_html(link):
    with open("tasks/assets/change_password.html") as file:
        file_str = "".join(file.readlines())
        file_str = file_str.format(link=link)
    return file_str


@celery_app.task
def send_reset_link(email: str, token: str):
    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.starttls()
        server.login(EmailSecret.EMAIL_ADRESS, EmailSecret.PASSWORD)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Pricetrack: change password"
        msg['From'] = EmailSecret.EMAIL_ADRESS
        msg['To'] = email

        # create the content of email
        url = CLIENT_URI + "/password-change/" + token
        html = get_change_password_html(url)

        msg.attach(MIMEText(html, "html"))
        server.sendmail(EmailSecret.EMAIL_ADRESS, "iamterec@gmail.com", msg.as_string())

    except SMTPAuthenticationError:
        print("Unable to authorize to SMTP server")

    except SMTPException:  # base SMTP exception
        print("Exception raised during SMTP connection")

    except Exception as e:
        print("Exception was rised during sending email: ", e)

