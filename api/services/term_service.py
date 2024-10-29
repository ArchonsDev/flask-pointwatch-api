from typing import Any, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.term import Term

from ..exceptions.validation import InvalidParameterError

class TermService:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_term(self, **data: dict[str, Any]) -> Term:
        term = Term()

        for key, value in data.items():
            if not hasattr(term, key):
                raise InvalidParameterError()
            
            setattr(term, key, value)

        self.db.session.add(term)
        self.db.session.commit()
        return term

    def get_term(self, filter_func: Callable[[Query, Term], Iterable]) -> Term:
        return filter_func(Term.query, Term)

    def update_term(self, term: Term, **data: dict[str, Any]) -> Term:
        for key, value in data.items():
            if not hasattr(term, key):
                raise InvalidParameterError(key)

            setattr(term, key, value)

        term.date_modified = datetime.now()
        self.db.session.commit()
        return term

    def delete_term(self, term: Term) -> None:
        self.update_term(term, is_deleted=True)
