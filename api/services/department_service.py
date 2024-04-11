from ..models import db

from ..models.department import Department
from ..models.user import User

def create_department(identity, data):
    requester = User.query.filter_by(email=identity).first()

    if not requester.is_admin:
        return "Unauthorized action.", 401
    
    code = data.get('code')
    name = data.get('name')

    existing_department_code = Department.query.filter_by(code=code).first()
    existing_department_name = Department.query.filter_by(name=name).first()

    if existing_department_code or existing_department_name:
        return "Department already exists", 409

    new_department = Department(
        code=code,
        name=name
    )

    db.session.add(new_department)
    db.session.commit()

    return {'message': "Department created."}, 200

def get_all_departments():
    departments = Department.query.all()
    return {'departments': [department.to_dict() for department in departments]}, 200
