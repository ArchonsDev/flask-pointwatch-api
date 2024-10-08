from datetime import datetime
from typing import Any

from .. import db

class User(db.Model):
    __tablename__ = 'tblusers'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    is_ms_linked = db.Column(db.Boolean, nullable=False, default=False)

    employee_id = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    # Link to SWTDForm
    swtd_forms = db.relationship('SWTDForm', backref='author', lazy=True)
    # Link to SWTDValidation
    validated_forms = db.relationship('SWTDValidation', backref='validator', lazy=True)
    # Link to SWTDComment
    comments = db.relationship('SWTDComment', backref='author', lazy=True)
    # For Point tracking
    point_balance = db.Column(db.Float, nullable=False, default=0)
    # For Department Head
    headed_department = db.relationship("Department", foreign_keys="Department.head_id", back_populates="head")
    # For department membership
    department_id = db.Column(db.Integer, db.ForeignKey("tbldepartments.id"))
    department = db.relationship("Department", foreign_keys=[department_id], back_populates="members")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date_created": self.date_created.strftime("%m-%d-%Y %H:%M"),
            "date_modified": self.date_modified.strftime("%m-%d-%Y %H:%M"),
            "is_deleted": self.is_deleted,
            "is_ms_linked": self.is_ms_linked,
            "employee_id": self.employee_id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname":  self.lastname,
            "password": self.password,
            "department": self.department.to_dict() if self.department else None,
            "is_staff": self.is_staff,
            "is_admin": self.is_admin,
            "is_superuser": self.is_superuser,
            "point_balance": self.point_balance
        }
