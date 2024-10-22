from datetime import datetime
from typing import Any

from .. import db

class Proof(db.Model):
    __tablename__ = "tblproofs"

    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Proof Metadata
    path = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.Text, nullable=False)

    # Foreign Key
    swtd_form_id = db.Column(db.Integer, db.ForeignKey("tblswtdforms.id"), nullable=False)

    # Relationships
    swtd_form = db.relationship("SWTDForm", foreign_keys=[swtd_form_id], back_populates="proof", uselist=False, lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "path": self.path,
            "filename": self.filename,
            "content_type": self.content_type
        }
