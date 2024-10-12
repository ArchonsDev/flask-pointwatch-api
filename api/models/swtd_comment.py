from typing import Any
from datetime import datetime

from .. import db

class SWTDComment(db.Model):
    __tablename__ = 'tblswtdcomments'

    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Comment Data
    message = db.Column(db.String(255), nullable=False)

    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    swtd_id = db.Column(db.Integer, db.ForeignKey('tblswtdforms.id'), nullable=False)

    # Relationship
    author = db.relationship("User", foreign_keys=[author_id], back_populates="comments", uselist=False, lazy=True)
    swtd_form = db.relationship("SWTDForm", foreign_keys=[swtd_id], back_populates="comments", lazy=True)

    @property
    def is_edited(self) -> bool:
        return self.date_created != self.date_modified

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Comment Data
            "message": self.message,
            "is_edited": self.is_edited
        }
