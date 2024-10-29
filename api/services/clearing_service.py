from typing import Any, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.clearing import Clearing

from ..exceptions.validation import InvalidParameterError

class ClearingService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_clearing(self, **data: dict[str, Any]) -> Clearing:
        clearing = Clearing()

        for key, value in data.items():
            if not hasattr(Clearing, key):
                raise InvalidParameterError(key)
            
            setattr(clearing, key, value)

        self.db.session.add(clearing)
        self.db.session.commit()
        return clearing

    def get_clearing(self, filter_func: Callable[[Query, Clearing], Iterable]) -> Clearing:
        return filter_func(Clearing.query, Clearing)

    def update_clearing(self, clearing: Clearing, **data: dict[str, Any]) -> Clearing:
        for key, value in data.items():
            if not hasattr(clearing, key):
                raise InvalidParameterError(key)

            setattr(clearing, key, value)

        clearing.date_modified = datetime.now()
        self.db.session.commit()
        return clearing
    
    def delete_clearing(self, clearing) -> None:
        self.update_clearing(clearing, is_deleted=True)
