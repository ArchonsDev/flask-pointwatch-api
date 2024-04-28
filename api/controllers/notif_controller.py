from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services.notif_service import notification_service

notif_bp = Blueprint('notif', __name__, url_prefix='/notifications')

@notif_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = request.jwt_identity.get('id')
    notifications, code = notification_service.get_notifications(user_id)
    return build_response(notifications, code)

@notif_bp.route('/<int:notif_id>', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notif_id):
    user_id = request.jwt_identity.get('id')
    success, code = notification_service.mark_notification_as_read(user_id, notif_id)
    if success:
        return build_response({"message": "Notification marked as read successfully."}, code)
    else:
        return build_response({"error": "Notification not found or you don't have permission to mark it as read."}, code)
