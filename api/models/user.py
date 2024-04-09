from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=True)
    lastname = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, id, employee_id, email, firstname, lastname, password, department, is_admin):
        self.id = id
        self.employee_id = employee_id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.department = department
        self.is_admin = is_admin

    def __repr__(self):
        return self.email
