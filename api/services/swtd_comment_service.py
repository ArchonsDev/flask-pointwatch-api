from datetime import datetime

from ..models import db
from ..models.swtd_comment import SWTDComment

def create_comment(swtd, author, message):
    comment = SWTDComment(
        author_id=author.id,
        swtd_id=swtd.id,
        message=message,
        date_modified=datetime.now(),
    )

    db.session.add(comment)
    db.session.commit()

def update_comment(comment, message):
    comment.message = message
    db.session.commit()

def delete_comment(comment):
    comment.is_deleted = True
    db.session.commit()
