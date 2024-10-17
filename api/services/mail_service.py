import os
from typing import Any

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

        mail_body = mail_template.format(reset_link=os.getenv("APP_URL"), username=firstname, token=token)
        self.send_mail('Account Recovery | PointWatch', [email,], mail_body)

    def send_swtd_validation_mail(self, email: str, **data: dict[str, Any]) -> None:
        with current_app.open_resource('templates/validation_update_template.txt', 'r') as f:
            mail_template = f.read()

        mail_body = mail_template.format(
            firstname=data.get("firstname"),
            swtd_id=data.get("swtd_id"),
            title=data.get("title"),
            date_created=data.get("date_created").strftime("%d %B %Y %I:%M %p"),
            status=data.get("status"),
            validation_date=data.get("validation_date").strftime("%d %B %Y %I:%M %p"),
            validator_name=data.get("validator_name"),
            app_url=os.getenv("APP_URL")
        )

        self.send_mail('SWTD Validation Update | PointWatch', [email,], mail_body)

    def send_clearance_update_mail(self, email: str, **data: dict[str, Any]) -> None:
        with current_app.open_resource('templates/clearing_granted_template.txt', 'r') as f:
            mail_template = f.read()

        mail_body = mail_template.format(
            firstname=data.get("firstname"),
            term_name=data.get("term_name"),
            date_created=data.get("date_created").strftime("%d %B %Y %I:%M %p"),
            clearer_name=data.get("clearer_name")
        )

        self.send_mail('Term Clearance Update | PointWatch', [email,], mail_body)
