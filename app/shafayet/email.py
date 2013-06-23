from flask.ext.mail import Message
from app import mail
from decorators import async

@async
def send_async_email(msg):
    mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body=None):
    msg = Message(subject, sender=sender, recipients=recipients)
    if not text_body is None:
        msg.body = text_body
    msg.body = text_body
    if not html_body is None:
        msg.html = html_body
    #TODO: Debug RuntimeError: working outside of application context
    #send_async_email(msg)
    mail.send(msg)

