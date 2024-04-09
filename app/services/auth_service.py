from flask import jsonify
from .sql_service import MySQLPool
import bcrypt

conn = MySQLPool()

class AuthService:
    @staticmethod
    def create_account(data):
        pass

    @staticmethod
    def login(data):
        pass

    @staticmethod
    def encode(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    @staticmethod
    def check_password(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed)