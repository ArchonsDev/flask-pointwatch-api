from sqlalchemy import event
from datetime import datetime

from ..models.notification import Notification
from ..models.swtd_validation import SWTDValidation
from ..models.clearing import Clearing
from ..exceptions import InvalidParameterError

class NotificationService:
    def __init__(self, db, socketio, term_service, user_service):
        self.db = db
        self.socketio = socketio
        self.term_service = term_service
        self.user_service = user_service

        self.init_event_handlers()

    def init_event_handlers(self):
        event.listen(SWTDValidation, 'after_update', self.handle_after_update_swtd_validation)
        event.listen(Clearing, 'after_insert', self.handle_after_insert_clearing)
        event.listen(Clearing, 'after_delete', self.handle_after_delete_clearing)

    def trigger_ws_event(self, event, data=None):
        self.socketio.emit(event, data, namespace='/notifications')

    def handle_after_update_swtd_validation(self, mapper, connection, swtd_validation: SWTDValidation):
        actor = swtd_validation.validator if swtd_validation.validator else swtd_validation.form.author
        target = swtd_validation.form.author
        
        data = {
            "title": swtd_validation.form.title,
            "status": swtd_validation.status
        }

        notification = self.create_notification(
            actor.id,
            target.id,
            data
        )

        self.trigger_ws_event('swtd_validation_update', notification.to_dict())

    def handle_after_insert_clearing(self, mapper, connection, clearing: Clearing):
        actor = self.user_service.get_user(id=clearing.cleared_by)
        target = self.user_service.get_user(id=clearing.user_id)
        term = self.term_service.get_term(clearing.term_id)

        notification = self.create_notification(
            actor.id,
            target.id,
            term.to_dict()
        )

        self.trigger_ws_event('term_clearing_update', notification.to_dict())

    def handle_after_delete_clearing(self, mapper, connection, clearing: Clearing):
        actor = self.user_service.get_user(id=clearing.cleared_by)
        target = self.user_service.get_user(id=clearing.user_id)
        term = self.term_service.get_term(clearing.term_id)

        notification = self.create_notification(
            actor.id,
            target.id,
            term.to_dict()
        )

        self.trigger_ws_event('term_clearing_update', notification.to_dict())

    def create_notification(self, actor_id, target_id, data):
        notification = Notification(
            actor_id=actor_id,
            target_id=target_id,
            data=data,
            date=datetime.now(),
            is_deleted=False,
            is_viewed=False
        )

        self.db.session.add(notification)

        return notification

    def update_notification(self, notification, **data):
        for key, value in data.items():
            if not hasattr(Notification, key):
                raise InvalidParameterError(key)
            
            setattr(notification, key, value)

        self.db.session.commit()
