from typing import Union, Any, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.term import Term
from ..exceptions import InvalidParameterError

class TermService:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def check_date_availability(self, start_date: str, end_date: str) -> bool:
        overlapping_terms = Term.query.filter(
            (Term.start_date <= end_date) &
            (Term.end_date >= start_date) &
            (Term.is_deleted == False)
        ).all()
        
        return True if overlapping_terms else False

    def create_term(self, name: str, start_date: str, end_date: str, type: str) -> Term:
        term = Term(
            name=name,
            start_date=start_date,
            end_date=end_date,
            type=type.strip().upper()
        )

        self.db.session.add(term)
        self.db.session.commit()
        return term

    def get_term(self, filter_func: Callable[[Query, Term], Iterable]) -> Term:
        return filter_func(Term.query, Term)

    def update_term(self, term: Term, **data: dict[str, Any]) -> Term:
        allowed_fields = [
            "name",
            "start_date",
            "end_date",
            "type"
        ]

        for field in allowed_fields:
            value = data.get(field)

            if value is None:
                continue

            if field == "type":
                value = value.strip().upper()

            setattr(term, field, value)

        term.date_modified = datetime.now()
        self.db.session.commit()
        return term

    def delete_term(self, term: Term) -> None:
        term.is_deleted = True
        term.date_modified = datetime.now()
        self.db.session.commit()
