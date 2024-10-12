from datetime import datetime
from typing import Union, Any, Callable, Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

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

    def get_department(self, filter_func: Callable[[Query, Department], Iterable]):
        return filter_func(Department.query, Department)

    def update_department(self, department: Department, **data: dict[str, Any]) -> Department:
        updated_fields = {
            "name": data.get("name"),
            "classification": data.get("classification"),
            "has_midyear": data.get("has_midyear")
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
