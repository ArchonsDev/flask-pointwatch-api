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

def get_comment_by_id(id):
    comment = SWTDComment.query.get(id)

    if comment and comment.is_deleted:
        return None
    
    return comment

def get_all_swtd_comments(swtd_form):
    comments = swtd_form.comments
    return list(filter(lambda comment: comment.is_deleted == False, comments))

def update_comment(comment, message):
    comment.message = message
    comment.date_modified = datetime.now()
    comment.is_edited = True
    db.session.commit()

def delete_comment(comment):
    comment.is_deleted = True
    db.session.commit()
