from typing import Union, Any

from flask_sqlalchemy import SQLAlchemy

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

    def create_term(self, name: str, start_date: str, end_date: str, **data) -> Term:
        term = Term(
            name=name,
            start_date=start_date,
            end_date=end_date,
            **data
        )

        self.db.session.add(term)
        self.db.session.commit()
        return term

    def get_term(self, id: int) -> Union[Term, None]:
        return Term.query.get(id)

    def get_all_terms(self, **params: dict[str, Any]) -> list[Term]:
        term_query = Term.query

        for key, value in params.items():
            # Skip 'is_deleted' paramters.
            if key == 'is_deleted':
                continue

            if not hasattr(Term, key):
                raise InvalidParameterError(key)
            
            if type(value) is str:
                term_query = term_query.filter(getattr(Term, key).like(f'%{value}%'))
            else:
                term_query = term_query.filter(getattr(Term, key) == value)

        return term_query.all()

    def update_term(self, term: Term, **data: dict[str, Any]) -> Term:
        for key, value in data.items():
            # Ensure provided key is valid.
            if not hasattr(Term, key):
                raise InvalidParameterError(key)

            setattr(term, key, value)

        self.db.session.commit()
        return term

    def delete_term(self, term: Term) -> None:
        term.is_deleted = True
        self.db.session.commit()
