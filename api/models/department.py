from . import db

class Department(db.Model):
    __tablename__ = 'tbldepartments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    users = db.relationship('User', back_populates='department', lazy=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'members': [user.email for user in self.users]
        }
