from datetime import datetime

from .. import db

class SWTDComment(db.Model):
    __tablename__ = 'tblswtdcomments'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False)
    swtd_id = db.Column(db.Integer, db.ForeignKey('tblswtdforms.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_edited = db.Column(db.Boolean, nullable=False, default=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "author": self.author.to_dict(),
            "date_modified": self.date_modified.strftime('%m-%d-%Y %H:%M:%S'),
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted
        }
