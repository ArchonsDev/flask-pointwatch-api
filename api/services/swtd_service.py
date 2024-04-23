from datetime import datetime
from sqlalchemy.exc import IntegrityError

from ..models import db
from ..models.swtd_form import SWTDForm

def get_all_swtds(params=None):
    swtd_query = SWTDForm.query

    try:
        for key, value in params.items():
            if key == 'is_deleted':
                continue

            if not hasattr(SWTDForm, key):
                return f'Invalid parameter: {key}', 400
            
            swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}'))
        
        return swtd_query.all(), 200
    except AttributeError:
        return 'One or more query parameters are invalid.', 400

def create_swtd(data):
    author_id = data.get('author_id')
    title = data.get('title')
    venue = data.get('venue')
    category = data.get('category')
    role = data.get('role')
    date_str = data.get('date')
    time_started_str = data.get('time_started')
    time_finished_str = data.get('time_finished')
    points = data.get('points')
    benefits = data.get('benefits')

    try:
        date = datetime.strptime(date_str, '%m-%d-%Y').date() if date_str else None
        time_started = datetime.strptime(time_started_str, '%H:%M').time() if time_started_str else None
        time_finished = datetime.strptime(time_finished_str, '%H:%M').time() if time_finished_str else None
    except Exception:
        return {'error': 'Incorrect time or date format.'}, 400

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

    try:
        db.session.commit()
    except IntegrityError:
        return 'One or more required fields are missing', 400

    return swtd_form, 200

def get_swtd(id):
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return "SWTD form not found.", 404

    return swtd_form, 200

def update_swtd(id, data):
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return {'error': 'SWTD form not found.'}, 404
  
    if 'title' in data:
        swtd_form.title = data.get('title')
    if 'venue' in data:
        swtd_form.venue = data.get('venue')
    if 'category' in data:
        swtd_form.venu = data.get('category')
    if 'role' in data:
        swtd_form.role = data.get('role')

    try:
        if 'date' in data:
            date_str = data.get('date')
            date = datetime.strptime(date_str, '%m-%d-%Y').date() if date_str else None
            swtd_form.date = date
        if 'time_started' in data:
            time_started_str = data.get('time_started')
            time_started = datetime.strptime(time_started_str, '%H:%M').time() if time_started_str else None
            swtd_form.time_started = time_started
        if 'time_finished' in data:
            time_finished_str = data.get('time_finished')
            time_finished = datetime.strptime(time_finished_str, '%H:%M').time() if time_finished_str else None
            swtd_form.time_finished = time_finished
    except Exception:
        return 'Incorrect time or date format.', 400
    
    if 'points' in data:
        swtd_form.points = data.get('points')
    if 'benefits' in data:
        swtd_form.benefits = data.get('benefits')

    try:
        db.session.commit()
    except IntegrityError:
        return 'One or more required fields are missing', 400

    return swtd_form, 200

def delete_swtd(id):
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return {'error': 'SWTD form not found.'}, 404

    if swtd_form.is_deleted:
        return {'error': 'SWTD form already deleted.'}, 404
    
    swtd_form.is_deleted = True

    db.session.commit()
    return {'message': 'SWTD form deleted.'}, 200
