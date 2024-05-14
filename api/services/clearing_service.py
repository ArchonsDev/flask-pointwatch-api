from __future__ import annotations
from typing import Optional

from flask_sqlalchemy import SQLAlchemy

from ..models.clearing import Clearing

class ClearingService(object):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def create_clearing(self, user_id: int, term_id: int, cleared_by: int, **data) -> Clearing:
        clearing = Clearing(
            user_id=user_id,
            term_id=term_id,
            cleared_by=cleared_by,
            **data
        )

        self.db.session.add(clearing)
        self.db.session.commit()

        return clearing
    
    def get_clearing_by_id(self, id: int) -> Optional[Clearing]:
        return Clearing.query.get(id)
    
    def get_user_term_clearing(self, user_id: int, term_id: int) -> Optional[Clearing]:
        return Clearing.query.filter((Clearing.user_id == user_id) & (Clearing.term_id == term_id)).first()

    def delete_clearing(self, id: int) -> None:
        clearing = self.get_clearing_by_id(id)

        if clearing:
            self.db.session.delete(clearing)
            self.db.session.commit()
