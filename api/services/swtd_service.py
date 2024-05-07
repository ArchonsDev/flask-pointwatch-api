from . import term_service
from ..exceptions import InvalidParameterError, TermNotFoundError
from ..models import db
from ..models.swtd_form import SWTDForm

def get_all_swtds(params=None):
    swtd_query = SWTDForm.query

    for key, value in params.items():
        # Skip 'is_deleted' param.
        if key == 'is_deleted':
            continue

        if not hasattr(SWTDForm, key):
            raise InvalidParameterError(key)
        
        if type(value) is str:
            swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}%'))
        else:
            swtd_query = swtd_query.filter(getattr(SWTDForm, key) == value)

    swtds = swtd_query.all()
    return list(filter(lambda swtd_form: swtd_form.is_deleted == False, swtds))

def create_swtd(author_id, title, venue, category, role, date, time_started, time_finished, points, benefits, term):
    swtd_form = SWTDForm(
        author_id=author_id,
        title=title,
        venue=venue,
        category=category,
        role=role,
        date=date,
        time_started=time_started,
        time_finished=time_finished,
        points=points,
        benefits=benefits,
        term=term
    )

    db.session.add(swtd_form)
    db.session.commit()

    return swtd_form

def get_swtd(id):
    swtd_form = SWTDForm.query.get(id)
    # Do not return SWTD if marked as deleted.
    if swtd_form and swtd_form.is_deleted:
        return None
    
    return swtd_form

def update_swtd(swtd_form, **data):
    for key, value in data.items():
        # Ensure provided key is valid.
        if not hasattr(SWTDForm, key):
            raise InvalidParameterError(key)

        if key == 'term_id':
            term = term_service.get_term(value)

            if not term:
                raise TermNotFoundError()
            
            swtd_form.term = term
        else:            
            setattr(swtd_form, key, value)

    db.session.commit()
    return swtd_form

def delete_swtd(swtd_form):
    swtd_form.is_deleted = True
    db.session.commit()
