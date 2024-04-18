from models import FormEntry
from app import db

def create_entry(title, venue, category, role, date, time_started, time_finished, points):
    if any(field is None for field in [title, venue, category, role, date, time_started, time_finished, points]):
        return {'error': "All fields must be filled in."}, 400

    new_entry = FormEntry(
        title=title,
        venue=venue,
        category=category,
        role=role,
        date=date,
        time_started=time_started,
        time_finished=time_finished,
        points=points
    )

    db.session.add(new_entry)
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