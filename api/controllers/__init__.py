from .auth_controller import auth_bp
from .user_controller import user_bp
from .swtd_controller import swtd_bp

blueprints = [
    auth_bp,
    user_bp,
    swtd_bp
]
