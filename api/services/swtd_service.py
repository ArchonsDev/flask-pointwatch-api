from flask import current_app

from ..models.form import Form
from ..models import db

def create_entry(data):

    title = data.get('title'),
    venue = data.get('venue'),
    category = data.get('venue'),
    role = data.get('role'),
    date = data.get('date'),
    time_started = data.get('time_started'),
    time_finished = data.get('time_started'),
    points = data.get('points')


    form = Form(
        title=title,
        venue=venue,
        category = category,
        role=role,
        date=date,
        time_started=time_started,
        time_finished=time_finished,
        points = points

    )
    

    db.session.add(form)
    db.session.commit()

    return {'message': "Form entry created successfully."}, 201

def get_entry(entry_id):
    entry = FormEntry.query.get(entry_id)
    if entry:
        return entry
    else:
        return {'error': 'Entry not found'}, 404

def update_entry(entry_id, title, venue, category, role, date, time_started, time_finished, points):
    entry = FormEntry.query.get(entry_id)
    if not entry:
        return {'error': 'Entry not found'}, 404

    entry.title = title
    entry.venue = venue
    entry.category = category
    entry.role = role
    entry.date = date
    entry.time_started = time_started
    entry.time_finished = time_finished
    entry.points = points
    db.session.commit()

    return {'message': "Form entry updated successfully."}, 200

def delete_entry(entry_id):
    entry = FormEntry.query.get(entry_id)
    if not entry:
        return {'error': 'Entry not found'}, 404

    db.session.delete(entry)
    db.session.commit()

    return {'message': "Form entry deleted successfully."}, 204