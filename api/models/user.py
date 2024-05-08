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

    def calculate_points(self):
        swtds = self.swtd_forms
        validated_points = 0
        unvalidated_points = 0
        rejected_points = 0

        for form in swtds:
            if form.is_deleted:
                continue
            
            status = form.validation.status
            
            if status == 'APPROVED':
                validated_points += form.points
            elif status == 'REJECTED':
                rejected_points += form.points
            elif status == 'PENDING':
                unvalidated_points += form.points

        return {
            "valid_points": validated_points,
            "pending_points": unvalidated_points,
            "invalid_points": rejected_points
        }

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
            "is_ms_linked": self.ms_user is not None,
            "is_deleted": self.is_deleted,
            "swtd_points": self.calculate_points()
        }
