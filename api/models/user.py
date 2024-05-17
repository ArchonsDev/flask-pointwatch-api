from typing import Any

from .. import db

class User(db.Model):
    __tablename__ = 'tblusers'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=True)
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    # Link to SWTDForm
    swtd_forms = db.relationship('SWTDForm', backref='author', lazy=True)
    # Link to MSUser
    ms_user = db.relationship('MSUser', backref='user', lazy=True, uselist=False)
    # Link to SWTDValidation
    validated_forms = db.relationship('SWTDValidation', backref='validator', lazy=True)
    # Link to SWTDComment
    comments = db.relationship('SWTDComment', backref='author', lazy=True)
    # For Point tracking
    point_balance = db.Column(db.Float, nullable=False, default=0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "email": self.email,
            "firstname": self.firstname,
            "lastname":  self.lastname,
            "password": self.password,
            "department": self.department,
            "is_staff": self.is_staff,
            "is_admin": self.is_admin,
            "is_superuser": self.is_superuser,
            "is_ms_linked": self.ms_user is not None,
            "is_deleted": self.is_deleted,
            "point_balance": self.point_balance
        }
