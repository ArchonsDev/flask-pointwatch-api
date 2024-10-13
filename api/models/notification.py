from typing import Any
from datetime import datetime

from .. import db

class Notification(db.Model):
    __tablename__ = 'tblnotifications'

    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Notification Data
    data = db.Column(db.JSON, nullable=False)
    is_viewed = db.Column(db.Boolean, nullable=False, default=False)

    # Foreign Keys
    actor_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)

    # Relationships
    actor = db.relationship("User", foreign_keys=[actor_id], back_populates="triggered_notifications", uselist=False, lazy=True)
    target = db.relationship("User", foreign_keys=[target_id], back_populates="received_notifications", uselist=False, lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-$d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            "data": self.data,
            "is_viewed": self.is_viewed
        }
