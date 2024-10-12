import os

from flask import current_app
from flask_mail import Message, Mail

from ..services.jwt_service import JWTService

class MailService:
    def __init__(self, mail: Mail, jwt_service: JWTService) -> None:
        self.mail = mail
        self.jwt_service = jwt_service

    def send_mail(self, subject: str, recipients: list[str], body: str) -> None:
        msg = Message(subject, sender='mail.wildpark@gmail.com', recipients=recipients)
        msg.body = body

        self.mail.send(msg)

    def send_recovery_mail(self, email: str, firstname: str) -> None:
        token = self.jwt_service.generate_token(email)

        with current_app.open_resource('templates/account_recovery_instructions_template.txt', 'r') as f:
            mail_template = f.read()

        mail_body = mail_template.format(reset_link=os.get_env("APP_URL"), username=firstname, token=token)
        self.send_mail('Account Recovery | PointWatch', [email,], mail_body)
