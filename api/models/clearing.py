from datetime import datetime
from typing import Any

from .. import db

class Clearing(db.Model):
    __tablename__ = 'tblclearings'

    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Clearing Data
    applied_points = db.Column(db.Float, nullable=False, default=0)

    # Foreign Keys
    clearer_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('tblterms.id'), nullable=False)

    # Relationships
    clearer = db.relationship('User', foreign_keys=[clearer_id], back_populates="clearings", uselist=False, lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], back_populates="clearances", uselist=False, lazy=True)
    term = db.relationship('Term', foreign_keys=[term_id], back_populates="clearances", uselist=False, lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Clearing Data
            "applied_points": self.applied_points,

            "clearer": self.clearer.to_dict(),
            "user": {
                "id": self.user.id,
                "firstname": self.user.firstname,
                "lastname": self.user.lastname,
                "employee_id": self.user.employee_id
            },
            "term": {
                "id": self.term.id,
                "name": self.term.name
            }
        }
