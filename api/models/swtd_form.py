from typing import Any

from .. import db

class SWTDForm(db.Model):
    __tablename__ = 'tblswtdforms'
    
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    dates = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Float, nullable=False)
    benefits = db.Column(db.String(2000), nullable=False)
    has_deliverables = db.Column(db.Boolean, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    term_id = db.Column(db.Integer, db.ForeignKey('tblterms.id'), nullable=False)
    # Link to SWTDValidation
    validation = db.relationship('SWTDValidation', backref='form', uselist=False, lazy=True)
    # Link to SWTDComment
    comments = db.relationship('SWTDComment', backref='swtd_form', lazy=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "venue": self.venue,
            "category": self.category,
            "role": self.role,
            "dates": self.dates_to_json(),
            "points": self.points,
            "benefits": self.benefits,
            "has_deliverables": self.has_deliverables,
            "is_deleted": self.is_deleted,
            "validation": self.validation.to_dict() if self.validation else None,
            "term": self.term.to_dict()
        }

    @staticmethod
    def dates_to_str(dates) -> str:
        date_str = "".join(
            f"{date.get("date")} {date.get("time_started")}-{date.get("time_ended")},"
            for date in dates
        )

        return date_str[:-1]

    def dates_to_json(self) -> dict[str, str]:
        dateset = []

        dates = self.dates.split(",")
        for d in dates:
            date, time = d.split(' ')

            time_started, time_ended = time.split('-')

            dateset.append(
                {
                    "date": date,
                    "time_started": time_started,
                    "time_ended": time_ended
                }
            )

        return dateset
