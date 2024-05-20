from typing import Any
from datetime import datetime

from .. import db

class Term(db.Model):
    __tablename__ = 'tblterms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_sem = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    # Link to SWTDForm
    swtd_forms = db.relationship('SWTDForm', backref='term', lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.strftime("%m-%d-%Y"),
            "end_date": self.end_date.strftime("%m-%d-%Y"),
            "is_sem": self.is_sem,
            "is_ongoing": self.start_date <= datetime.now().date() and self.end_date >= datetime.now().date()
        }
