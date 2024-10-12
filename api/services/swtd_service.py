from typing import Any, Union
from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy

from ..models.swtd_form import SWTDForm
from ..models.term import Term
from ..models.proof import Proof
from ..services.term_service import TermService
from ..exceptions import InvalidParameterError, TermNotFoundError

class SWTDService:
    def __init__(self, db: SQLAlchemy, term_service: TermService) -> None:
        self.db = db
        self.term_service = term_service

    def get_all_swtds(self, params: dict[str, Any]=None) -> list[SWTDForm]:
        swtd_query = SWTDForm.query

        for key, value in params.items():
            # Skip 'is_deleted' param.
            if key == 'is_deleted':
                continue

            if not hasattr(SWTDForm, key):
                raise InvalidParameterError(key)
            
            if type(value) is str:
                swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}%'))
            else:
                swtd_query = swtd_query.filter(getattr(SWTDForm, key) == value)

        return swtd_query.all()

    def create_swtd(self, author_id: int, title: str, venue: str, category: str, role: str, dates: str, points: int, benefits: str, has_deliverables: bool, term: Term) -> SWTDForm:
        swtd_form = SWTDForm(
            author_id=author_id,
            title=title,
            venue=venue,
            category=category,
            role=role,
            dates=SWTDForm.dates_to_str(json.loads(dates)),
            points=points,
            benefits=benefits,
            has_deliverables=True if has_deliverables.lower().startswith("true") else False,
            term=term
        )

        self.db.session.add(swtd_form)
        self.db.session.commit()

        return swtd_form

    def get_swtd(self, id: int) -> Union[SWTDForm, None]:
        return SWTDForm.query.get(id)

    def update_swtd(self, swtd_form: SWTDForm, **data: dict[str, Any]) -> SWTDForm:
        for key, value in data.items():
            # Ensure provided key is valid.
            if not hasattr(SWTDForm, key):
                raise InvalidParameterError(key)

            if key == "dates":
                value = SWTDForm.dates_to_str(value)

            if key == 'term_id':
                term = self.term_service.get_term(value)

                if not term:
                    raise TermNotFoundError()
                
                swtd_form.term = term

            setattr(swtd_form, key, value)

        self.db.session.commit()
        return swtd_form

    def delete_swtd(self, swtd_form: SWTDForm) -> None:
        swtd_form.is_deleted = True
        self.db.session.commit()
