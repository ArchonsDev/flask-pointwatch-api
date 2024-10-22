from typing import Any, Union, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.swtd_form import SWTDForm
from ..services.term_service import TermService

class SWTDService:
    def __init__(self, db: SQLAlchemy, term_service: TermService) -> None:
        self.db = db
        self.term_service = term_service

    def create_swtd(self, **data: dict[str, Any]) -> SWTDForm:
        swtd_form = SWTDForm(
            title=data.get("title"),
            venue=data.get("venue"),
            category=data.get("category"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            total_hours=data.get("total_hours"),
            points=data.get("points"),
            benefits=data.get("benefits"),
            author_id=data.get("author_id"),
            term_id=data.get("term_id")
        )

        self.db.session.add(swtd_form)
        self.db.session.commit()
        return swtd_form

    def get_swtd(self, filter_func: Callable[[Query, SWTDForm], Iterable]) -> Union[SWTDForm, None]:
        return filter_func(SWTDForm.query, SWTDForm)

    def update_swtd(self, swtd_form: SWTDForm, **data: dict[str, Any]) -> SWTDForm:
        allowed_fields = [
            "title",
            "venue",
            "category",
            "start_date",
            "end_date",
            "total_hours",
            "points",
            "benefits",
            "term_id",
            "validation_status",
            "validator_id",
            "date_validated",
            "is_deleted"
        ]

        for field in allowed_fields:
            value = data.get(field)

            if value == None:
                continue

            if field == "validation_status" and value == "PENDING":
                swtd_form.date_validated = None
                swtd_form.validator_id = None

            setattr(swtd_form, field, value)

        swtd_form.date_modified = datetime.now()
        self.db.session.commit()
        return swtd_form

    def delete_swtd(self, swtd_form):
        self.update_swtd(swtd_form, is_deleted=True)
