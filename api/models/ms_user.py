from . import db

class MSUSer(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.ForeignKey, nullable=False)
    access_token = db.Column(db.String(1000), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "acess_token": self.access_token
        }
