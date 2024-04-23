from . import db

class User(db.Model):
    __tablename__ = 'tblusers'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_staff = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    forms = db.relationship('SWTDForm', backref='user', lazy=True)
    ms_token = db.Column(db.String(1000), nullable=True)

    def to_dict(self):
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
            "is_deleted": self.is_deleted
        }
