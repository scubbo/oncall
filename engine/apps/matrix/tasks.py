import asyncio

from celery.utils.log import get_task_logger
from django.conf import settings

from apps.alerts.models import AlertGroup
from apps.user_management.models import User
from common.custom_celery_tasks import shared_dedicated_queue_retry_task

from .client import MatrixClient



MAX_RETRIES = 1 if settings.DEBUG else 10
logger = get_task_logger(__name__)

logger.fatal("DEBUGGGGGGG - here")
client = MatrixClient.login_with_username_and_password(
    settings.MATRIX_USER_ID,
    settings.MATRIX_PASSWORD,
    "temporary-grafana-device-id",
    settings.MATRIX_HOMESERVER
)


@shared_dedicated_queue_retry_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=MAX_RETRIES)
def notify_user_via_celery(user_pk, alert_group_pk, notification_policy_pk):
    # imported here to avoid circular import error
    from apps.base.models import UserNotificationPolicy, UserNotificationPolicyLogRecord

    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        logger.warning(f"User {user_pk} does not exist")
        return

    try:
        alert_group = AlertGroup.all_objects.get(pk=alert_group_pk)
    except AlertGroup.DoesNotExist:
        logger.warning(f"Alert group {alert_group_pk} does not exist")
        return

    try:
        notification_policy = UserNotificationPolicy.objects.get(pk=notification_policy_pk)
    except UserNotificationPolicy.DoesNotExist:
        logger.warning(f"User notification policy {notification_policy_pk} does not exist")
        return

    if not user.matrix_user_identity:
        UserNotificationPolicyLogRecord.objects.create(
            author=user,
            type=UserNotificationPolicyLogRecord.TYPE_PERSONAL_NOTIFICATION_FAILED,
            notification_policy=notification_policy,
            alert_group=alert_group,
            reason="Error while sending Matrix message",
            notification_step=notification_policy.step,
            notification_channel=notification_policy.notify_by
        )
        logger.error("Error while sending Matrix message: no User Identity to send to")
        return


    asyncio.run(client.send_message_to_room_id(settings.MATRIX_ROOM_ID, f"New version - notify {user.matrix_user_identity}"))

