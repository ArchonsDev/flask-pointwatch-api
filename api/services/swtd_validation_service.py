from datetime import datetime

from ..models import db
from ..models.swtd_validation import SWTDValidation

def create_validation(swtd, proof):
    validation = SWTDValidation(
        swtd_id=swtd.id,
        proof=proof,
        validated_on=datetime.utcnow
    )

    db.session.add(validation)
    db.session.commit()

def update_validation(swtd, user, valid=None):
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

    db.session.commit()
