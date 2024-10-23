from typing import Any
from datetime import datetime

from .. import db

class SWTDForm(db.Model):
    __tablename__ = 'tblswtdforms'
    
    # Record Information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Form Data
    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Float, nullable=False)
    points = db.Column(db.Float, nullable=False)
    benefits = db.Column(db.Text, nullable=False)

    # Form Validation
    date_validated = db.Column(db.DateTime)
    validation_status = db.Column(db.String(255), nullable=False, default="PENDING")

    # Foreign Keys
    author_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('tblterms.id'), nullable=False)
    validator_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'))

    # Relationships
    author = db.relationship("User", foreign_keys=[author_id], back_populates="swtd_forms", uselist=False, lazy=True)
    comments = db.relationship("SWTDComment", foreign_keys="SWTDComment.swtd_id", back_populates="swtd_form", lazy=True)
    proof = db.relationship("Proof", foreign_keys="Proof.swtd_form_id", back_populates="swtd_form", lazy=True)
    term = db.relationship("Term", foreign_keys=[term_id], back_populates="swtd_forms", uselist=False, lazy=True)
    validator = db.relationship("User", foreign_keys=[validator_id], back_populates="validated_swtd_forms", uselist=False, lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Form Data
            "title": self.title,
            "venue": self.venue,
            "category": self.category,
            "start_date": self.start_date.strftime("%m-%d-%Y"),
            "end_date": self.end_date.strftime("%m-%d-%Y"),
            "total_hours": self.total_hours,
            "points": self.points,
            "benefits": self.benefits,

            # Form Validation
            "date_validated": self.date_validated.strftime("%m-%d-%Y %H:%M") if self.date_validated else None,
            "validation_status": self.validation_status,

            "author": self.author.to_dict()
        }
