from typing import Any, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.clearing import Clearing

class ClearingService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_clearing(self, **data: dict[str, Any]) -> Clearing:
        clearing = Clearing(
            user_id=data.get("user_id"),
            term_id=data.get("term_id"),
            clearer_id=data.get("clearer_id"),
            applied_points=data.get("applied_points")
        )

        self.db.session.add(clearing)
        self.db.session.commit()
        return clearing

    def get_clearing(self, filter_func: Callable[[Query, Clearing], Iterable]) -> Clearing:
        return filter_func(Clearing.query, Clearing)

    def update_clearing(self, clearing: Clearing, **data: dict[str, Any]) -> Clearing:
        allowed_fields = [
            "user_id",
            "term_id",
            "clearer_id",
            "is_deleted",
            "applied_points"
        ]

        for field in allowed_fields:
            value = data.get(field)

            if value is None:
                continue

            setattr(clearing, field, value)

        clearing.date_modified = datetime.now()
        self.db.session.commit()
        return clearing
    
    def delete_clearing(self, clearing) -> None:
        self.update_clearing(clearing, is_deleted=True)
