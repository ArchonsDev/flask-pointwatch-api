from . import db

class Form(db.Model):
    __tablename__ = 'tblform'

    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=True)
    date = db.Column(db.String(255), nullable=True)
    time_started = db.Column(db.String(255), nullable=False)
    time_finished = db.Column(db.String(255))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

  

    def to_dict(self):
        return {
            "title": self.title,
            "venue": self.venue,
            "role": self.role,
            "date": self.date,
            "time_started":  self.time_started,
            "time_finished": self.time_finished,
            "is_deleted": self.is_deleted,
        }