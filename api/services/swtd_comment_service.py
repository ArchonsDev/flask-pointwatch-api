from datetime import datetime

from ..models.swtd_comment import SWTDComment

class SWTDCommentService:
    def __init__(self, db):
        self.db = db

    def create_comment(self, swtd, author, message):
        comment = SWTDComment(
            author_id=author.id,
            swtd_id=swtd.id,
            message=message,
            date_modified=datetime.now(),
        )

        self.db.session.add(comment)
        self.db.session.commit()

    def get_comment_by_id(self, id):
        return SWTDComment.query.get(id)

    def update_comment(self, comment, message):
        comment.message = message
        comment.date_modified = datetime.now()
        comment.is_edited = True
        self.db.session.commit()

    def delete_comment(self, comment):
        comment.is_deleted = True
        self.db.session.commit()
