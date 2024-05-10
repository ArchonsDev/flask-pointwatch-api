from .. import db
class MSUser(db.Model):
    __tablename__ = 'tblmsusers'

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False, unique=True)
    access_token = db.Column(db.TEXT, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id
        }
