from datetime import datetime

from ..models import db
from ..models.swtd_validation import SWTDValidation

def create_validation(swtd, proof):
    validation = SWTDValidation(
        swtd_id=swtd.id,
        proof=proof,
        validated_on=datetime.utcnow
    )

    swtd.validation = validation
    db.session.commit()
