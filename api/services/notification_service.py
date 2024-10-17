from typing import Any
from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Mapper
from sqlalchemy.engine import Connection
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from ..models.notification import Notification
from ..models.clearing import Clearing
from ..models.swtd_form import SWTDForm

from ..services.term_service import TermService
from ..services.user_service import UserService
from ..services.mail_service import MailService

from ..exceptions import InvalidParameterError

class NotificationService:
    def __init__(self, db: SQLAlchemy, socketio: SocketIO, term_service: TermService, user_service: UserService, mail_service: MailService) -> None:
        self.db = db
        self.socketio = socketio
        self.term_service = term_service
        self.user_service = user_service
        self.mail_service = mail_service

        self.init_event_handlers()

    def init_event_handlers(self) -> None:
        event.listen(SWTDForm, 'after_update', self.handle_after_update_swtd)
        event.listen(Clearing, 'after_insert', self.handle_after_insert_clearing)

    def trigger_ws_event(self, event: str, data: dict[str, Any]=None) -> None:
        self.socketio.emit(event, data, namespace='/notifications')

    def handle_after_update_swtd(self, mapper: Mapper, connection: Connection, swtd_form: SWTDForm) -> None:
        actor = swtd_form.validator if swtd_form.validator else swtd_form.author
        target = swtd_form.author
        
        data = {
            "title": swtd_form.title,
            "status": swtd_form.validation_status
        }

        notification = self.create_notification(
            actor_id=actor.id,
            target_id=target.id,
            content=data
        )

        if swtd_form.validation_status != "PENDING":
            self.mail_service.send_swtd_validation_mail(
                swtd_form.author.email,
                firstname=swtd_form.author.firstname,
                swtd_id=swtd_form.id,
                title=swtd_form.title,
                date_created=swtd_form.date_created,
                status=swtd_form.validation_status,
                validation_date=swtd_form.date_validated,
                validator_name=f"{swtd_form.validator.firstname} {swtd_form.validator.lastname}",
            )

        self.trigger_ws_event('swtd_validation_update', notification.to_dict())

    def handle_after_insert_clearing(self, mapper: Mapper, connection: Connection, clearing: Clearing) -> None:
        actor = self.user_service.get_user(lambda q, u: q.filter_by(id=clearing.clearer_id).first())
        target = self.user_service.get_user(lambda q, u: q.filter_by(id=clearing.user_id).first())
        term = self.term_service.get_term(lambda q, t: q.filter_by(id=clearing.term_id).first())

        notification = self.create_notification(
            actor_id=actor.id,
            target_id=target.id,
            content=term.to_dict()
        )

        self.mail_service.send_clearance_update_mail(
            target.email,
            firstname=target.firstname,
            term_name=term.name,
            date_created=clearing.date_created,
            clearer_name=f"{actor.firstname} {actor.lastname}"
        )

        self.trigger_ws_event('term_clearing_update', notification.to_dict())

    def create_notification(self, **data: dict[str, Any]) -> Notification:
        notification = Notification(
            date_created=datetime.now(),
            actor_id=data.get("actor_id"),
            target_id=data.get("target_id"),
            data=data.get("content")
        )

        self.db.session.add(notification)
        return notification

    def update_notification(self, notification: Notification, **data: dict[str, Any]) -> None:
        for key, value in data.items():
            if not hasattr(Notification, key):
                raise InvalidParameterError(key)
            
            setattr(notification, key, value)

        self.db.session.commit()
