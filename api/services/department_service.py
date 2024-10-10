from datetime import datetime
from typing import Union, Any

from flask_sqlalchemy import SQLAlchemy

from ..models.department import Department

class DepartmentService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_department(self, name: str, required_points: int, classification: str, has_midyear: bool) -> Department:
        department = Department(
            name=name,
            required_points=required_points,
            classification=classification,
            has_midyear=has_midyear
        )

        self.db.session.add(department)
        self.db.session.commit()
        return department

    def get_department(self, id: int) -> Union[Department, None]:
        return Department.query.get(id)

    def get_all_departments(self, **params: dict[str, Any]) -> list[Department]:
        department_query = Department.query

        for key, value in params.items():
            # Skip 'is_deleted' paramters.
            if key == 'is_deleted':
                continue

            if not hasattr(Department, key):
                raise InvalidParameterError(key)
            
            if type(value) is str:
                department_query = department_query.filter(getattr(Department, key).like(f'%{value}%'))
            else:
                department_query = department_query.filter(getattr(Department, key) == value)

        return department_query.all()

    def update_department(self, department: Department, **data: dict[str, Any]) -> Department:
        updated_fields = {
            "name": data.get("name"),
            "classification": data.get("classification"),
            "has_midyear": data.get("has_midyear"),
            "head_id": data.get("head_id")
        }

        for key, value in updated_fields.items():
            # Ensure provided key is valid.
            if not hasattr(Department, key):
                raise InvalidParameterError(key)

            setattr(department, key, value)

        department.date_modified = datetime.now()
        self.db.session.commit()
        return department

    def delete_department(self, department: Department) -> None:
        department.is_deleted = True
        department.date_modified = datetime.now()
        self.db.session.commit()
