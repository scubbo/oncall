import asyncio

from celery.utils.log import get_task_logger
from django.conf import settings

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
logger.fatal("DEBUGGGGGGG - now here")


@shared_dedicated_queue_retry_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=MAX_RETRIES)
def notify_user_via_celery(user_pk, alert_group_pk, notification_policy_pk):
    print('\n\n\n=====================\n=====================\n\n'
          'Congratulations! You triggered a task!\n'
          'Now get to work building the Matrix client so the task can actually do something :P'
          '\n\n=====================\n=====================\n\n\n')
    asyncio.run(client.send_message_to_room_id(settings.MATRIX_ROOM_ID, f"Notify {user_pk}"))

