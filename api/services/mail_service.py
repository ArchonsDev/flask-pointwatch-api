from flask import current_app
from flask_mail import Message

class MailService:
    def __init__(self, mail, jwt_service):
        self.mail = mail
        self.jwt_service = jwt_service

def send_mail(self, subject, recipients, body):
    msg = Message(subject, sender='mail.wildpark@gmail.com', recipients=recipients)
    msg.body = body

    self.mail.send(msg)

def send_recovery_mail(self, email, firstname):
    token = self.jwt_service.generate_token(email)

    with current_app.open_resource('templates/account_recovery_instructions_template.txt', 'r') as f:
        mail_template = f.read()

    mail_body = mail_template.format(username=firstname, token=token)
    send_mail('Account Recovery | PointWatch', [email,], mail_body)
