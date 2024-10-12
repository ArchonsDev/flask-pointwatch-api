from datetime import datetime

from .. import db

class Proof(db.Model):
    __tablename__ = "tblproofs"

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    swtd_form_id = db.Column(db.Integer, db.ForeignKey("tblswtdforms.id"), nullable=False)
    swtd_form = db.relationship("SWTDForm", foreign_keys=[swtd_form_id], back_populates="proof", uselist=False, lazy=True)
