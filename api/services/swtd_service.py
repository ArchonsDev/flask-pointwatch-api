from datetime import datetime
from sqlalchemy.exc import IntegrityError

from ..models import db
from ..models.swtd_form import SWTDForm
from ..models.user import User

def get_all_swtds(identity, params=None):
    requester = User.query.filter_by(email=identity).first()
    author_id = params.get('author_id')

    if author_id:
        author_id = int(author_id)

    # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
    if (author_id is not None and
            requester.id != author_id and not (
                requester.is_staff or requester.is_admin or requester.is_superuser
            )
    ) or (
        author_id is None and not (
            requester.is_staff or requester.is_admin or requester.is_superuser
        )
    ):
        return {"error": "Insufficient permissions. Cannot retrieve SWTD Forms."}, 403

    swtd_query = SWTDForm.query

    if not params:
        swtd_forms = swtd_query.filter_by(is_deleted=False).all()
    else:
        try:
            for key, value in params.items():
                if not hasattr(SWTDForm, key):
                    return {'error': f'Invalid parameter: {key}'}, 400
                
                swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}'))
            
            swtd_forms = swtd_query.all()
        except AttributeError:
            return {'error': 'One or more query parameters are invalid.'}, 400
        
    return {"swtd_forms": [swtd_form.to_dict() for swtd_form in swtd_forms]}, 200

def create_swtd(identity, data):
    requester = User.query.filter_by(email=identity).first()

    author_id = requester.id
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
        return {'error': 'One or more required fields are missing'}, 400

    return {'message': 'SWTD form submitted.'}, 200

def get_swtd(identity, id):
    requester = User.query.filter_by(email=identity).first()
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return {'error': "SWTD form not found."}, 404
    
    if swtd_form.is_deleted:
        return {'error': "SWTD form not found."}, 404

    if swtd_form.author_id != requester.id and not (requester.is_staff or requester.is_admin or requester.is_superuser):
        return {'error': "Insufficient permissions. Cannot retrive SWTD Form data."}, 403
    
    return {'swtd_form': swtd_form.to_dict()}, 200

def update_swtd(identity, id, data):
    requester = User.query.filter_by(email=identity).first()
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return {'error': 'SWTD form not found.'}, 404
    
    if swtd_form.author_id != requester.id and not (requester.is_staff or requester.is_admin or requester.is_superuser):
        return {'error': 'Insufficient permissions. Cannot update SWTD Form.'}, 400

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
        return {'error': 'Incorrect time or date format.'}, 400
    
    if 'points' in data:
        swtd_form.points = data.get('points')
    if 'benefits' in data:
        swtd_form.benefits = data.get('benefits')

    try:
        db.session.commit()
    except IntegrityError:
        return {'error': 'One or more required fields are missing'}, 400

    return {'message': 'SWTD form updated.'}, 200

def delete_swtd(identity, id):
    requester = User.query.filter_by(email=identity).first()
    swtd_form = SWTDForm.query.get(id)

    if not swtd_form:
        return {'error': 'SWTD form not found.'}, 404
    
    if swtd_form.author_id != requester.id and not (requester.is_staff or requester.is_admin or requester.is_superuser):
        return {'error': 'Insufficient permissions. Cannot update SWTD Form.'}, 400

    if swtd_form.is_deleted:
        return {'error': 'SWTD form already deleted.'}, 404
    
    swtd_form.is_deleted = True

    db.session.commit()
    return {'message': 'SWTD form deleted.'}, 200
