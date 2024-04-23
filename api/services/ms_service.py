from . import oauth

def get_user_data(token):
    response = oauth.microsoft.get('https://graph.microsoft.com/v1.0/me', token=token)

    if not response.status_code == 200:
        return {'error': "Failed to retrieve user data."}, 500
    
    user_info = response.json()

    return user_info, 200
