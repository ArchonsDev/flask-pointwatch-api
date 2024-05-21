from typing import Union, Any

import json
from flask_sqlalchemy import SQLAlchemy

from ..models.point_summary import PointSummary
from ..models.swtd_form import SWTDForm
from ..models.term import Term
from ..models.user import User
from ..services.password_encoder_service import PasswordEncoderService
from ..services.clearing_service import ClearingService
from ..exceptions import InvalidParameterError, InsufficientSWTDPointsError, TermClearingError

class UserService:
    def __init__(self, db: SQLAlchemy, password_encoder_service: PasswordEncoderService, clearing_service: ClearingService) -> None:
        self.db = db
        self.password_encoder_service = password_encoder_service
        self.clearing_service = clearing_service

    def create_user(self, employee_id: str, email: str, firstname: str, lastname: str, password: str, department: str=None) -> User:
        user = User(
            employee_id=employee_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=self.password_encoder_service.encode_password(password),
            department=department
        )
        
        self.db.session.add(user)
        self.db.session.commit()

        return user

    def get_user(self, id: int=None, email: str=None, employee_id: str=None) -> Union[User, None]:
        query = User.query

        if employee_id:
            return query.filter_by(employee_id=employee_id).first()

        if email:
            return query.filter_by(email=email).first()
        
        user = query.get(id)

        return user

    def get_all_users(self, params: dict[str, Any]={}) -> list[User]:
        user_query = User.query

        for key, value in params.items():
            # Ensure provided key is valid.
            if not hasattr(User, key):
                raise InvalidParameterError(key)

            if type(key) is str:
                user_query = user_query.filter(getattr(User, key).like(f'%{value}%'))
            else:
                user_query = user_query.filter(getattr(User, key) == value)
  
        return user_query.all()

    def update_user(self, user: User, **data: dict[str, Any]) -> User:
        for key, value in data.items():
            # Ensure provided key is valid.
            if not hasattr(User, key):
                raise InvalidParameterError(key)
            
            if key == 'password':
                value = self.password_encoder_service.encode_password(value)

            setattr(user, key, value)

        self.db.session.commit()
        return user
    
    def delete_user(self, user) -> None:
        user.is_deleted = True
        self.db.session.commit()

    def get_user_swtd_forms(self, user: User, start_date: str=None, end_date: str=None) -> list[SWTDForm]:
        swtd_forms = user.swtd_forms

        if start_date:
            swtd_forms = list(filter(lambda form: form.date >= start_date, swtd_forms))

        if end_date:
            swtd_forms = list(filter(lambda form: form.date <= end_date, swtd_forms))

        return swtd_forms

    def get_point_summary(self, user: User, term: Term) -> PointSummary:
        swtd_forms = list(filter(
            lambda form: (form.is_deleted == False) & 
            (form.date >= term.start_date) & 
            (form.date <= term.end_date) &
            (form.author_id == user.id),
            term.swtd_forms
        ))

        points = PointSummary()

        # Compute VALID, PENDING, and INVALID points
        for form in swtd_forms:
            status = form.validation.status

            if status == 'APPROVED':
                points.valid_points += form.points
            elif status == 'PENDING':
                points.pending_points += form.points
            elif status == 'REJECTED':
                points.invalid_points += form.points

        # Compute LACKING points
        with open('point_requirements.json', 'r') as f:
            points.required_points = json.load(f).get(user.department, 0)

        return points
    
    def get_term_summary(self, user: User, term: Term) -> dict[str, Any]:
        points = self.get_point_summary(user, term)
        clearing = self.clearing_service.get_user_term_clearing(user.id, term.id)

        return {
            "is_cleared": clearing is not None,
            "points": points
        }

    def clear_user_for_term(self, user: User, target: User, term: Term) -> None:
        if self.clearing_service.get_user_term_clearing(target.id, term.id):
            raise TermClearingError("User already cleared for this term.")

        points = self.get_point_summary(target, term)

        available_points = points.valid_points + target.point_balance
        if available_points < points.required_points:
            raise InsufficientSWTDPointsError(points.lacking_points)
        
        target.point_balance += points.excess_points - points.lacking_points

        self.clearing_service.create_clearing(
            target.id,
            term.id,
            user.id,
            applied_points=points.lacking_points
        )

    def unclear_user_for_term(self, target: User, term: Term) -> None:
        points = self.get_point_summary(target, term)

        clearing = self.clearing_service.get_user_term_clearing(target.id, term.id)
        if not clearing:
            raise TermClearingError("User has not been cleared for this term.")

        target.point_balance -= points.excess_points - clearing.applied_points

        self.db.session.delete(clearing)
        self.db.session.commit()
