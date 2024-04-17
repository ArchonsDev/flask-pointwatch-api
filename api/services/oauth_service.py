import requests

def get_user_data(token):
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers={
        'Authorization': f'Bearer {token.get("access_token")}'
    })

    if not response.status_code == 200:
        return {'error': "Failed to retrieve user data."}, 500
    
    user_info = response.json()

    return user_info, 200
