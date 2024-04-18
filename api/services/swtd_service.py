from models import FormEntry
from app import db

class FormService:
    @staticmethod
    def create_entry(title, venue, category, role, date, time_started, time_finished, points):
        
        # Ensure that all fields are present
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

        return {'message': "Successfully created."}, 200

    @staticmethod
    def get_entry(entry_id):
        return FormEntry.query.get(entry_id)

    @staticmethod
    def update_entry(entry_id, title, venue, category, role, date, time_started, time_finished, points):
        entry = FormEntry.query.get(entry_id)
        entry.title = title
        entry.venue = venue
        entry.category = category
        entry.role = role
        entry.date = date
        entry.time_started = time_started
        entry.time_finished = time_finished
        entry.points = points
        db.session.commit()
        return entry

    @staticmethod
    def delete_entry(entry_id):
        entry = FormEntry.query.get(entry_id)
        db.session.delete(entry)
        db.session.commit()