from ..models import db

from ..models.department import Department
from ..models.user import User

def create_department(identity, data):
    requester = User.query.filter_by(email=identity).first()

    # Ensure that the requester is an HRD admin.
    if not requester.is_admin:
        return "Insufficient permissions. Cannot create Department", 403
    
    code = data.get('code')
    name = data.get('name')

    existing_department_code = Department.query.filter_by(code=code).first()
    existing_department_name = Department.query.filter_by(name=name).first()

    # Ensure that the department code or name is not in use.
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
    departments = Department.query.filter_by(is_deleted=False).all()
    return {'departments': [department.to_dict() for department in departments]}, 200

def get_department(department_id):
    existing_department = Department.query.get(department_id)

    # Ensure that the department exists.
    if not existing_department:
        return "Department not found.", 404
    
    return existing_department.to_dict(), 200

def update_department(identity, department_id, data):
    requester = User.query.filter_by(email=identity).first()

    # Ensure that the requester is an HRD admin.
    if not requester.is_admin:
        return "Insufficient permissions. Cannot update Department information.", 403
    
    existing_department = Department.query.get(department_id)

    # Ensure that the target department exists.
    if not existing_department:
        return "Department not found", 404
    
    if 'code' in data:
        code = data.get('code')

        existing_department_code = Department.query.filter_by(code=code).first()

        # Ensure that the new code is not in use.
        if existing_department_code:
            return "Department code already in use.", 409
        
        existing_department.code = code
    if 'name' in data:
        name = data.get('name')

        existing_department_name = Department.query.filter_by(name=name).first()

        # Ensure that the new name is not in use.
        if existing_department_name:
            return "Department name already in use.", 409
        
        existing_department.name = name

        db.session.commit()

    return "Department updated.", 200

def delete_department(identity, department_id):
    requester = User.query.filter_by(email=identity)

    # Ensure that the requester is an HRD admin.
    if not requester.is_admin:
        return "Insufficient permissions. Cannot delete department.", 403
    
    existing_department = Department.query.get(department_id)

    # Ensure that the target department exists.
    if not existing_department:
        return "Department not found.", 404
    
    # Ensure that the target department is not deleted.
    if existing_department.is_deleted:
        return "Department already deleted.", 409
    
    existing_department.is_deleted = True

    db.session.commit()
    return "Department deleted.", 200
