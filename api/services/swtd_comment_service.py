from typing import Iterable, Callable, Any
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.swtd_comment import SWTDComment

from ..exceptions.validation import InvalidParameterError

class SWTDCommentService:
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_comment(self, **data: dict[str, Any]) -> None:
        comment = SWTDComment()

        for key, value in data.items():
            if not hasattr(comment, key):
                raise InvalidParameterError(key)
            
            setattr(comment, key, value)

        self.db.session.add(comment)
        self.db.session.commit()
        return comment

    def get_comment(self, filter_func: Callable[[Query, SWTDComment], Iterable]) -> SWTDComment:
        return filter_func(SWTDComment.query, SWTDComment)

    def update_comment(self, comment: SWTDComment, **data: dict[str, Any]) -> None:
        for key, value in data.items():
            if not hasattr(comment, key):
                raise InvalidParameterError(key)
            
            setattr(comment, key, value)

        comment.date_modified = datetime.now()
        self.db.session.commit()
        return comment

    def delete_comment(self, comment: SWTDComment) -> None:
        self.update_comment(comment, is_deleted=True)
