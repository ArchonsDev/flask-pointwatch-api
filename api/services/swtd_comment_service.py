from typing import Union
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from ..models.swtd_form import SWTDForm
from ..models.swtd_comment import SWTDComment
from ..models.user import User

class SWTDCommentService:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_comment(self, swtd: SWTDForm, author: User, message: str) -> None:
        comment = SWTDComment(
            author_id=author.id,
            swtd_id=swtd.id,
            message=message,
            date_modified=datetime.now(),
        )

        self.db.session.add(comment)
        self.db.session.commit()

    def get_comment_by_id(self, id: int) -> Union[SWTDComment, None]:
        return SWTDComment.query.get(id)

    def update_comment(self, comment: SWTDComment, message: str) -> None:
        comment.message = message
        comment.date_modified = datetime.now()
        comment.is_edited = True
        self.db.session.commit()

    def delete_comment(self, comment: SWTDComment) -> None:
        comment.is_deleted = True
        self.db.session.commit()
