from datetime import datetime
from typing import Union, Any, Callable, Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.department import Department

class DepartmentService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_department(self, name: str, required_points: float, level: str, midyear_points: float, use_schoolyear: bool) -> Department:
        department = Department(
            name=name,
            required_points=required_points,
            level=level.strip().upper(),
            midyear_points=midyear_points,
            use_schoolyear=use_schoolyear
        )

        self.db.session.add(department)
        self.db.session.commit()
        return department

    def get_department(self, filter_func: Callable[[Query, Department], Iterable]):
        return filter_func(Department.query, Department)

    def update_department(self, department: Department, **data: dict[str, Any]) -> Department:
        allowed_fields = {
            "name",
            "required_points",
            "level",
            "midyear_points",
            "use_schoolyear",
            "head"
        }

        for field in allowed_fields:
            value = data.get(field)

            if value is None:
                continue

            if field == "head" and value.access_level < 1:
                value.access_level = 1

            if field == "level":
                value = value.strip().upper()

            setattr(department, field, value)

        department.date_modified = datetime.now()
        self.db.session.commit()
        return department

    def delete_department(self, department: Department) -> None:
        for u in department.members:
            u.department_id = None

        department.is_deleted = True
        department.date_modified = datetime.now()
        self.db.session.commit()