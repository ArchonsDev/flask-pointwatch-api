import json

from ..models.user import User
from ..models.clearing import Clearing
from ..exceptions import InvalidParameterError

class UserService:
    def __init__(self, db, password_encoder_service):
        self.db = db
        self.password_encoder_service = password_encoder_service

    def create_user(self, employee_id, email, firstname, lastname, password, department=None):
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

    def get_user(self, id=None, email=None, employee_id=None):
        query = User.query

        if employee_id:
            return query.filter_by(employee_id=employee_id).first()

        if email:
            return query.filter_by(email=email).first()
        
        user = query.get(id)

        return user

    def get_all_users(self, params=None):
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

    def update_user(self, user, **data):
        for key, value in data.items():
            # Ensure provided key is valid.
            if not hasattr(User, key):
                raise InvalidParameterError(key)
            
            if key == 'password':
                value = self.password_encoder_service.encode_password(value)

            setattr(user, key, value)

        self.db.session.commit()
        return user
    
    def delete_user(self, user):   
        user.is_deleted = True
        self.db.session.commit()

    def get_user_swtd_forms(self, user, start_date=None, end_date=None):
        swtd_forms = user.swtd_forms

        if start_date:
            swtd_forms = list(filter(lambda form: form.date >= start_date, swtd_forms))

        if end_date:
            swtd_forms = list(filter(lambda form: form.date <= end_date, swtd_forms))

        return swtd_forms

    def get_point_summary(self, user, term):
        swtd_forms = term.swtd_forms
        swtd_forms = list(filter(lambda form: (form.is_deleted == False) & (form.date >= term.start_date) & (form.date <= term.end_date), swtd_forms))

        with open('point_requirements.json', 'r') as f:
            POINT_REQUIREMENTS = json.load(f)

        summary = {
            'valid_points': 0,
            'pending_points': 0,
            'invalid_points': 0,
        }

        # Compute VALID, PENDING, and INVALID points
        for form in swtd_forms:
            status = form.validation.status

            if status == 'APPROVED':
                summary['valid_points'] += form.points
            elif status == 'PENDING':
                summary['pending_points'] += form.points
            elif status == 'REJECTED':
                summary['invalid_points'] += form.points

        # Compute LACKING points
        required_points = POINT_REQUIREMENTS.get(user.department, 0)
        summary['required_points'] = required_points

        balance = summary['valid_points'] - required_points

        if balance > 0:
            summary['excess_points'] = balance
            summary['lacking_points'] = 0
        elif balance < 0:
            summary['excess_points'] = 0
            summary['lacking_points'] = balance * -1
        else:
            summary['excess_points'] = 0
            summary['lacking_points'] = 0

        return summary
    
    def clear_user_for_term(self, user, target, term):
        summary = self.get_point_summary(target, term)

        clearing = Clearing(
            user_id=target.id,
            term_id=term.id,
            cleared_by=user.id
        )

        self.db.session.add(clearing)

        excess_points = summary.get('excess_points', 0)

        if excess_points > 0:
            target.point_balance += excess_points

        self.db.session.commit()

    def unclear_user_for_term(self, target, term):
        summary = self.get_point_summary(target, term)

        clearing = Clearing.query.filter((Clearing.user_id == target.id) & (Clearing.term_id == term.id)).first()
        # TODO: Create custome exception
        if not clearing:
            return

        self.db.session.delete(clearing)

        excess_points = summary.get('excess_points', 0)

        if excess_points > 0:
            target.point_balance -= excess_points

        self.db.session.commit()
