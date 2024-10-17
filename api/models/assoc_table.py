from .. import db

department_head = db.Table('tbldepartmentheads',
    db.Column('user_id', db.Integer, db.ForeignKey("tblusers.id"), unique=True, primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey("tbldepartments.id"), unique=True, primary_key=True)
)
