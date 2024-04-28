from ..models import db
from ..models.notif import Notification

def get_notifications(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()
    if notifications:
        return [notif.to_dict() for notif in notifications], 200
    else:
        return {"error": "No notifications found for this user."}, 404

def mark_notification_as_read(user_id, notif_id):
    notification = Notification.query.get(notif_id)
    if notification and notification.user_id == user_id:
        notification.is_read = True
        db.session.commit()
        return True, 200
    else:
        return False, 404