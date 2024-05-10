from datetime import datetime

from .. import db

class Clearing(db.Model):
    __tablename__ = 'tblclearings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('tblterms.id'), nullable=False)
    date_cleared = db.Column(db.DateTime, nullable=False, default=datetime.now())
    cleared_by = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
