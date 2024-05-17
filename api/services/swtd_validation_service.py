from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage

from ..models.swtd_form import SWTDForm
from ..models.user import User
from ..models.swtd_validation import SWTDValidation
from ..services.ft_service import FTService

class SWTDValidatioNService:
    def __init__(self, db: SQLAlchemy, ft_service: FTService) -> None:
        self.db = db
        self.ft_service = ft_service

    def create_validation(self, swtd: SWTDForm, proof: str) -> None:
        validation = SWTDValidation(
            swtd_id=swtd.id,
            proof=proof
        )

        self.db.session.add(validation)
        self.db.session.commit()

    def update_validation(self, swtd: SWTDForm, user: User, valid: bool=None) -> None:
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

    def update_proof(self, swtd: SWTDForm, file: FileStorage) -> None:
        validation = swtd.validation

        self.ft_service.delete(swtd.author_id, swtd.id)

        validation.proof = file.filename
        self.db.session.commit()
