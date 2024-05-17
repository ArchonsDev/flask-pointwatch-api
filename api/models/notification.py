from typing import Any
from datetime import datetime

from .. import db

class Notification(db.Model):
    __tablename__ = 'tblnotifications'

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    date = db.Column(db.String(255), nullable=False, default=datetime.now())
    is_viewed = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'target_id': self.target_id,
            'data': self.data,
            'date': str(self.date),
            'is_viewed': self.is_viewed,
            'is_deleted': self.is_deleted
        }
