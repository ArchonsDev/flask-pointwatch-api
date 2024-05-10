from .. import db

class SWTDForm(db.Model):
    __tablename__ = 'tblswtdforms'
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_started = db.Column(db.Time, nullable=False)
    time_finished = db.Column(db.Time, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    benefits = db.Column(db.String(255), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    term_id = db.Column(db.Integer, db.ForeignKey('tblterms.id'), nullable=False)
    # Link to SWTDValidation
    validation = db.relationship('SWTDValidation', backref='form', uselist=False, lazy=True)
    # Link to SWTDComment
    comments = db.relationship('SWTDComment', backref='swtd_form', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "venue": self.venue,
            "category": self.category,
            "role": self.role,
            "date": self.date.strftime('%m-%d-%Y'),  # Convert date to string
            "time_started":  self.time_started.strftime('%H:%M'),  # Convert time to string
            "time_finished": self.time_finished.strftime('%H:%M'),  # Convert time to string
            "points": self.points,
            "benefits": self.benefits,
            "is_deleted": self.is_deleted,
            "validation": self.validation.to_dict() if self.validation else None,
            "term": self.term.to_dict()
        }
