from __future__ import annotations
from datetime import datetime
from typing import Any

from .. import db
from .assoc_table import department_head

class User(db.Model):
    __tablename__ = 'tblusers'

    # Record information
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Credentials
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Profile
    employee_id = db.Column(db.String(255), unique=True, nullable=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    point_balance = db.Column(db.Float, nullable=False, default=0)

    # Account Information
    is_ms_linked = db.Column(db.Boolean, nullable=False, default=False)
    access_level = db.Column(db.Integer, nullable=False, default=0)

    # Foreign Keys
    department_id = db.Column(db.Integer, db.ForeignKey("tbldepartments.id"))

    # Relationships
    clearances = db.relationship("Clearing", foreign_keys="Clearing.user_id", back_populates="user", lazy=True)
    clearings = db.relationship("Clearing", foreign_keys="Clearing.clearer_id", back_populates="clearer", lazy=True)
    comments = db.relationship("SWTDComment", foreign_keys="SWTDComment.author_id", back_populates="author", lazy=True)
    department = db.relationship("Department", foreign_keys=[department_id], back_populates="members", uselist=False, lazy=True)
    headed_department = db.relationship("Department", secondary=department_head, back_populates="head", uselist=False, lazy=True)
    swtd_forms = db.relationship("SWTDForm", foreign_keys="SWTDForm.author_id", back_populates="author", lazy=True)
    received_notifications = db.relationship("Notification", foreign_keys="Notification.target_id", back_populates="target", lazy=True)
    triggered_notifications = db.relationship("Notification", foreign_keys="Notification.actor_id", back_populates="actor", lazy=True)
    validated_swtd_forms = db.relationship("SWTDForm", foreign_keys="SWTDForm.validator_id", back_populates="validator", lazy=True)

    @property
    def is_head(self) -> bool:
        if not self.department:
            return False

        return self.department == self.headed_department

    @property
    def is_staff(self) -> bool:
        return self.access_level == 2

    @property
    def is_superuser(self) -> bool:
        return self.access_level == 3
    
    def is_head_of(self, user: User) -> bool:
        if not user.department:
            return False
        
        return user.department.head == self

    def to_dict(self) -> dict[str, Any]:
        return {
            # Record Information
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,

            # Credentials
            "email": self.email,

            # Profile
            "employee_id": self.employee_id,
            "firstname": self.firstname,
            "lastname":  self.lastname,
            "is_head": self.is_head,
            "is_staff": self.is_staff,
            "is_superuser": self.is_superuser,
            "point_balance": self.point_balance,

            # Account Information
            "is_ms_linked": self.is_ms_linked,
            "access_level": self.access_level
        }
