from .. import db

class SWTDValidation(db.Model):
    __tablename__ = 'tblswtdvalidations'

    swtd_id = db.Column(db.Integer, db.ForeignKey('tblswtdforms.id'), primary_key=True)
    proof = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False, default="PENDING")
    validator_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=True)
    validated_on = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "swtd_id": self.swtd_id,
            "status": self.status,
            "validator": self.validator.to_dict() if self.validator else None,
            "validated on": self.validated_on.strftime("%m-%d-%Y %H:%M") if self.validated_on else None
        }
