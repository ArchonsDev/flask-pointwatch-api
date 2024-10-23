from typing import Any, Union, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.swtd_form import SWTDForm
from ..services.term_service import TermService

from ..exceptions.validation import InvalidParameterError

class SWTDService:
    def __init__(self, db: SQLAlchemy, term_service: TermService) -> None:
        self.db = db
        self.term_service = term_service

    def create_swtd(self, **data: dict[str, Any]) -> SWTDForm:
        swtd_form = SWTDForm()

        for key, value in data.items():
            if not hasattr(swtd_form, key):
                raise InvalidParameterError(key)
            
            setattr(swtd_form, key, value)

        self.db.session.add(swtd_form)
        self.db.session.commit()
        return swtd_form

    def get_swtd(self, filter_func: Callable[[Query, SWTDForm], Iterable]) -> Union[SWTDForm, None]:
        return filter_func(SWTDForm.query, SWTDForm)

    def update_swtd(self, swtd_form: SWTDForm, **data: dict[str, Any]) -> SWTDForm:
        for key, value in data.items():
            if not hasattr(swtd_form, key):
                raise InvalidParameterError(key)
            
            setattr(swtd_form, key, value)

        swtd_form.date_modified = datetime.now()
        self.db.session.commit()
        return swtd_form

    def delete_swtd(self, swtd_form):
        self.update_swtd(swtd_form, is_deleted=True)
