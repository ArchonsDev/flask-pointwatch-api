from ..exceptions import InvalidParameterError
from ..models import db
from ..models.swtd_form import SWTDForm

def get_all_swtds(params=None):
    swtd_query = SWTDForm.query

    for key, value in params.items():
        if not hasattr(SWTDForm, key):
            raise InvalidParameterError(key)
        
        swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}'))
    
    return swtd_query.all()

def create_swtd(author_id, title, venue, category, role, date, time_started, time_finished, points, benefits):
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
        benefits=benefits
    )

    db.session.add(swtd_form)
    db.session.commit()

    return swtd_form

def get_swtd(id):
    return SWTDForm.query.get(id)

def update_swtd(swtd_form, **data):
    for key, value in data.items():
        # Ensure provided key is valid.
        if not hasattr(SWTDForm, key):
            raise InvalidParameterError(key)

        setattr(swtd_form, key, value)

    db.session.commit()
    return swtd_form

def delete_swtd(swtd_form):
    swtd_form.is_deleted = True
    db.session.commit()
