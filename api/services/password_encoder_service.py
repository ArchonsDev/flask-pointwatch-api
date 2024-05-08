import bcrypt

class PasswordEncoderService:
    def __init__(self):
        pass

    def encode_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def check_password(self, encoded_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), encoded_password.encode('utf-8'))
