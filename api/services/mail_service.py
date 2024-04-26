from flask import current_app
from flask_mail import Message

from . import mail, jwt_service

def send_mail(subject, recipients, body):
    msg = Message(subject, sender='mail.wildpark@gmail.com', recipients=recipients)
    msg.body = body

    mail.send(msg)

def send_recovery_mail(email, firstname):
    token = jwt_service.generate_token(email)

    with current_app.open_resource('templates/account_recovery_instructions_template.txt', 'r') as f:
        mail_template = f.read()

    mail_body = mail_template.format(username=firstname, token=token)
    send_mail('Account Recovery | PointWatch', [email,], mail_body)
