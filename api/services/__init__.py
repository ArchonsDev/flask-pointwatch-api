from .password_encoder_service import PasswordEncoderService
from .jwt_service import JWTService
from .auth_service import AuthService
from .ft_service import FTService
from .mail_service import MailService
from .user_service import UserService
from .ms_service import MSService
from .swtd_comment_service import SWTDCommentService
from .term_service import TermService
from .swtd_service import SWTDService
from .swtd_validation_service import SWTDValidatioNService
from .notification_service import NotificationService

from .. import db, oauth, mail, socketio

password_encoder_service = PasswordEncoderService()
jwt_service = JWTService()
auth_service = AuthService(password_encoder_service, jwt_service)
ft_service = FTService()
mail_service = MailService(mail, jwt_service)
user_service = UserService(db, password_encoder_service)
ms_service = MSService(db, oauth, user_service)
swtd_comment_service = SWTDCommentService(db)
term_service = TermService(db)
swtd_service = SWTDService(db, term_service)
swtd_validation_service = SWTDValidatioNService(db, ft_service)
notification_service = NotificationService(db, socketio, term_service, user_service)
