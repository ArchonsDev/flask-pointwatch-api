from . import db

class SWTDValidation(db.Model):
    __tablename__ = 'tblswtdvalidations'

    swtd_id = db.Column(db.Integer, db.ForeignKey('tblswtdforms.id'), primary_key=True)
    proof = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False, default="PENDING")
    validator_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=True)
