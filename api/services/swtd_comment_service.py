from typing import Iterable, Callable, Any
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.swtd_comment import SWTDComment

class SWTDCommentService:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_comment(self,**data: dict[str, Any]) -> None:
        comment = SWTDComment(
            author_id=data.get("author_id"),
            swtd_id=data.get("swtd_id"),
            message=data.get("message")
        )

        self.db.session.add(comment)
        self.db.session.commit()
        return comment

    def get_comment(self, filter_func: Callable[[Query, SWTDComment], Iterable]) -> SWTDComment:
        return filter_func(SWTDComment.query, SWTDComment)

    def update_comment(self, comment: SWTDComment, **data: dict[str, Any]) -> None:
        allowed_fields = [
            "message",
            "author_id",
            "swtd_id",
            "is_deleted"
        ]

        for field in allowed_fields:
            value = data.get(field)

            if value is None:
                continue

            setattr(comment, field, value)

        comment.date_modified = datetime.now()
        self.db.session.commit()
        return comment

    def delete_comment(self, comment: SWTDComment) -> None:
        self.update_comment(comment, is_deleted=True)
