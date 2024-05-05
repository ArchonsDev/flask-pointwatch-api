from ..models import db
from ..models.term import Term
from ..exceptions import InvalidParameterError

def check_date_availability(start_date, end_date):
    overlapping_terms = Term.query.filter(
        (Term.start_date <= end_date) &
        (Term.end_date >= start_date) &
        (Term.is_deleted == False)
    ).all()
    
    return True if overlapping_terms else False

def create_term(name, start_date, end_date):
    term = Term(
        name=name,
        start_date=start_date,
        end_date=end_date
    )

    db.session.add(term)
    db.session.commit()
    return term

def get_term(id):
    return Term.query.get(id)

def get_all_terms(params=None):
    term_query = Term.query

    for key, value in params.items():
        if not hasattr(Term, key):
            raise InvalidParameterError(key)
        
        if type(value) is str:
            term_query = term_query.filter(getattr(Term, key).like(f'%{value}%'))
        else:
            term_query = term_query.filter(getattr(Term, key) == value)
    
    return term_query.all()

def update_term(term, **data):
    for key, value in data.items():
        # Ensure provided key is valid.
        if not hasattr(Term, key):
            raise InvalidParameterError(key)

        setattr(term, key, value)

    db.session.commit()
    return term

def delete_term(term):
    term.is_deleted = True
    db.session.commit()
