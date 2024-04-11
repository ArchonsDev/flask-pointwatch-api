from ..models import db

from ..models.department import Department
from ..models.user import User

def create_department(identity, data):
    requester = User.query.filter_by(email=identity).first()

    if not requester.is_admin:
        return "Unauthorized action.", 401
    
    code = data.get('code')
    name = data.get('name')

    new_department = Department(
        code=code,
        name=name
    )

    db.session.add(new_department)
    db.session.commit()

    return "Department created.", 200

def get_all_departments():
    departments = Department.query.all()
    return {'departments': [department.to_dict() for department in departments]}, 200
