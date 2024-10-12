from typing import Any
from datetime import datetime

from .. import db

class Department(db.Model):
    __tablename__ = "tbldepartments"

    # Record Inormation
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Department Data
    name = db.Column(db.String(255), nullable=False)
    required_points = db.Column(db.Float, nullable=False)
    classification = db.Column(db.String(255), nullable=False)
    midyear_points = db.Column(db.Float, nullable=False)

    # Relationships
    members = db.relationship("User", foreign_keys="User.department_id", back_populates="department", lazy=True)

    @property
    def has_midyear(self) -> bool:
        return self.midyear_points > 0

    @property
    def head(self):
        return next((u for u in self.members if u.is_head), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Department Data
            "name": self.name,
            "required_points": self.required_points,
            "classification": self.classification,
            "midyear_points": self.midyear_points,
            "has_midyear": self.has_midyear
        }
