from ..models.term import Term
from ..exceptions import InvalidParameterError

class TermService:
    def __ini__(self, db):
        self.db = db

    def check_date_availability(self, start_date, end_date):
        overlapping_terms = Term.query.filter(
            (Term.start_date <= end_date) &
            (Term.end_date >= start_date) &
            (Term.is_deleted == False)
        ).all()
        
        return True if overlapping_terms else False

    def create_term(self, name, start_date, end_date):
        term = Term(
            name=name,
            start_date=start_date,
            end_date=end_date
        )

        self.db.session.add(term)
        self.db.session.commit()
        return term

    def get_term(self, id):
        term = Term.query.get(id)

        if term and term.is_deleted:
            return None
        
        return term

    def get_all_terms(self, params=None):
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

        terms = term_query.all()
        return list(filter(lambda term: term.is_deleted == False, terms))

    def update_term(self, term, **data):
        for key, value in data.items():
            # Ensure provided key is valid.
            if not hasattr(Term, key):
                raise InvalidParameterError(key)

            setattr(term, key, value)

        self.db.session.commit()
        return term

    def delete_term(self, term):
        term.is_deleted = True
        self.db.session.commit()
