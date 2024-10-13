from typing import Any
from datetime import datetime

from .. import db

class Term(db.Model):
    __tablename__ = 'tblterms'

    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Term Data
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(255), nullable=False)

    # Relationships
    swtd_forms = db.relationship("SWTDForm", foreign_keys="SWTDForm.term_id", back_populates='term', lazy=True)
    clearances = db.relationship("Clearing", foreign_keys="Clearing.term_id", back_populates="term", lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Term Data
            "name": self.name,
            "start_date": self.start_date.strftime("%m-%d-%Y"),
            "end_date": self.end_date.strftime("%m-%d-%Y"),
            "type": self.type,
            "is_ongoing": self.start_date <= datetime.now().date() and self.end_date >= datetime.now().date()
        }
