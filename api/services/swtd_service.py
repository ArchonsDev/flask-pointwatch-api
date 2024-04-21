from ..models import db
from ..models.swtd_form import SWTDForm
from ..models.user import User

def get_all_swtds(identity, params=None):
    requester = User.query.filter_by(email=identity).first()
    author_id = params.get('author_id')

    if author_id:
        author_id = int(author_id)

    # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
    if (
        author_id is not None and
            requester.id != author_id and not (
                requester.is_staff or requester.is_admin or requester.is_superuser
            )
        ) or \
    (
        author_id is None and not (
            requester.is_staff or requester.is_admin or requester.is_superuser
        )
    ):
        return {"error": "Insufficient permissions. Cannot retrieve SWTD Forms."}, 403

    swtd_query = SWTDForm.query

    if not params:
        swtd_forms = swtd_query.filter_by(is_deleted=False).all()
    else:
        try:
            for key, value in params.items():
                if not hasattr(SWTDForm, key):
                    return {'error': f'Invalid parameter: {key}'}, 400
                
                swtd_query = swtd_query.filter(getattr(SWTDForm, key).like(f'%{value}'))
            
            swtd_forms = swtd_query.all()
        except AttributeError:
            return {'error': 'One or more query parameters are invalid.'}, 400
        
    return {"swtd_forms": [swtd_form.to_dict() for swtd_form in swtd_forms]}, 200

def create_swtd(identity, data):
    pass

def get_swtd(identity, id):
    pass

def update_swtd(identity, id, data):
    pass

def delete_swtd(identity, id):
    pass
