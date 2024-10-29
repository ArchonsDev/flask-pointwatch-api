from datetime import datetime
from typing import Any, Callable, Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query
from sqlalchemy import delete

from ..models.department import Department
from ..models.assoc_table import department_head

from ..exceptions.validation import InvalidParameterError

class DepartmentService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_department(self, **data: dict[str, Any]) -> Department:
        department = Department()

        for key, value in data.items():
            if not hasattr(department, key):
                raise InvalidParameterError(key)
            
            setattr(department, key, value)

        self.db.session.add(department)
        self.db.session.commit()
        return department

    def get_department(self, filter_func: Callable[[Query, Department], Iterable]):
        return filter_func(Department.query, Department)

    def update_department(self, department: Department, **data: dict[str, Any]) -> Department:
        for key, value in data.items():
            if not hasattr(department, key):
                raise InvalidParameterError(key)

            setattr(department, key, value)

        department.date_modified = datetime.now()
        self.db.session.commit()
        return department

    def delete_department(self, department: Department) -> None:
        for u in department.members:
            u.department_id = None

        department.is_deleted = True
        department.date_modified = datetime.now()
        self.db.session.commit()
