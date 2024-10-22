from typing import Union, Any, Callable, Iterable
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query

from ..models.point_summary import PointSummary
from ..models.term import Term
from ..models.user import User

from ..services.password_encoder_service import PasswordEncoderService
from ..services.clearing_service import ClearingService

from ..exceptions import InsufficientSWTDPointsError, TermClearingError

class UserService:
    def __init__(self, db: SQLAlchemy, password_encoder_service: PasswordEncoderService, clearing_service: ClearingService) -> None:
        self.db = db
        self.password_encoder_service = password_encoder_service
        self.clearing_service = clearing_service

    # Create
    def create_user(self, **data: dict[str, Any]) -> User:
        user = User(
            # Credentials
            email=data.get("email"),
            password=self.password_encoder_service.encode_password(data.get("password")),

            # Profile
            employee_id=data.get("employee_id"),
            firstname=data.get("firstname"),
            lastname=data.get("lastname")
        )
        
        self.db.session.add(user)
        self.db.session.commit()

        return user

    # Read One
    def get_user(self, filter_func: Callable[[Query, User], Iterable]) -> Union[User, None]:
        return filter_func(User.query, User)

    # Update
    def update_user(self, user: User, **data: dict[str, Any]) -> User:
        allowed_fields = [
            "access_level",
            "department_id",
            "firstname",
            "is_deleted",
            "is_ms_linked",
            "lastname",
            "point_balance",
            "password"
        ]

        for field in allowed_fields:
            value = data.get(field)

            if value is None:
                continue

            if field == 'password':
                value = self.password_encoder_service.encode_password(value)

            setattr(user, field, value)

        user.date_modified = datetime.now()
        self.db.session.commit()
        return user
    
    def delete_user(self, user) -> None:
        self.update_user(user, is_deleted=True)

    def get_point_summary(self, user: User, term: Term) -> PointSummary:
        swtd_forms = list(filter(
            lambda form: (form.is_deleted == False) & 
            (form.start_date >= term.start_date) & 
            (form.start_date <= term.end_date) &
            (form.author == user),
            term.swtd_forms
        ))

        points = PointSummary()
        # Compute VALID, PENDING, and INVALID points
        for form in swtd_forms:
            status = form.validation_status

            if status == 'APPROVED':
                points.valid_points += form.points
            elif status == 'PENDING':
                points.pending_points += form.points
            elif status == 'REJECTED':
                points.invalid_points += form.points

        points.required_points = -1

        if user.department:
            if term.type == "MIDYEAR/SUMMER":
                points.required_points = user.department.midyear_points
            else:
                points.required_points = user.department.required_points

        return points
    
    def get_term_summary(self, user: User, term: Term) -> dict[str, Any]:
        points = self.get_point_summary(user, term)
        clearing = self.clearing_service.get_clearing(
            lambda q, c: q.filter_by(user_id=user.id, term_id=term.id, is_deleted=False).first()
        )

        return {
            "is_cleared": clearing is not None,
            "points": points
        }

    def grant_clearance(self, user: User, target: User, term: Term) -> None:
        if self.clearing_service.get_clearing(
            lambda q, c: q.filter_by(user_id=target.id, term_id=term.id, is_deleted=False).first()
        ):
            raise TermClearingError("User already cleared for this term.")

        points = self.get_point_summary(target, term)

        available_points = points.valid_points + target.point_balance
        if available_points < points.required_points:
            raise InsufficientSWTDPointsError(points.lacking_points)
        
        target.point_balance += points.excess_points - points.lacking_points
        target.date_modified = datetime.now()

        clearing = self.clearing_service.create_clearing(
            user_id=target.id,
            term_id=term.id,
            clearer_id=user.id,
            applied_points=points.lacking_points
        )

        return clearing

    def revoke_clearance(self, target: User, term: Term) -> None:
        points = self.get_point_summary(target, term)

        clearing = self.clearing_service.get_clearing(
            lambda q, c: q.filter_by(user_id=target.id, term_id=term.id, is_deleted=False).first()
        )
        if not clearing:
            raise TermClearingError("User has not been cleared for this term.")

        target.point_balance -= points.excess_points - clearing.applied_points
        target.date_modified = datetime.now()
        self.db.session.commit()

        clearing = self.clearing_service.update_clearing(clearing, is_deleted=True)
        return clearing
