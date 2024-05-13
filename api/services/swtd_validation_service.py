from datetime import datetime
from sqlalchemy import event

from ..models.swtd_validation import SWTDValidation

class SWTDValidatioNService:
    def __init__(self, db, socketio, ft_service):
        self.db = db
        self.socketio = socketio
        self.ft_service = ft_service

        self.init_event_handlers()

    def init_event_handlers(self):
        event.listen(SWTDValidation, 'after_update', self.handle_after_validation_update)

    def create_validation(self, swtd, proof):
        validation = SWTDValidation(
            swtd_id=swtd.id,
            proof=proof
        )

        self.db.session.add(validation)
        self.db.session.commit()

    def update_validation(self, swtd, user, valid=None):
        validation = swtd.validation

        if valid == True:
            validation.status = "APPROVED"
            validation.validator = user
            validation.validated_on = datetime.now()
        elif valid == False:
            validation.status = "REJECTED"
            validation.validator = user
            validation.validated_on = datetime.now()
        else:
            validation.status = "PENDING"
            validation.validator = None
            validation.validated_on = None

        self.db.session.commit()

    def update_proof(self, swtd, file):
        validation = swtd.validation

        self.ft_service.delete(swtd.author_id, swtd.id)

        validation.proof = file.filename
        self.db.session.commit()

    def handle_after_validation_update(self, mapper, connection, target: SWTDValidation):
        actor = target.validator
        author = target.form.author
        status = target.status
        swtd_id = target.swtd_id
        title = target.form.title

        self.socketio.emit(
            'swtd_validation_update',
            {
                'id': swtd_id,
                'title': title,
                'status': status,
                'actor': f'{actor.firstname} {actor.lastname}',
            },
            namespace=f'/'
        )
