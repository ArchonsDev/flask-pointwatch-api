from datetime import datetime

from ..models.swtd_validation import SWTDValidation

class SWTDValidatioNService:
    def __init__(self, db, ft_service):
        self.db = db
        self.ft_service = ft_service

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
