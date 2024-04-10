import bcrypt

class PasswordEncoderService:
    @staticmethod
    def encode_password(password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def check_password(encoded_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), encoded_password.encode('utf-8'))
