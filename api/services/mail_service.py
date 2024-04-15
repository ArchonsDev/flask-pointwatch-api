from flask_mail import Message

from . import mail

def send_mail(subject, recipients, body):
    msg = Message(subject, sender='mail.wildpark@gmail.com', recipients=recipients)
    msg.body = body
    mail.send(msg)
