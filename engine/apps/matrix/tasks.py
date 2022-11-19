import asyncio

from time import sleep
from typing import Optional

from celery.utils.log import get_task_logger
from django.conf import settings


from apps.alerts.models import AlertGroup
from apps.matrix.alert_rendering import build_message
from apps.matrix.client import MatrixClient
from apps.matrix.models import MatrixUserIdentity
from apps.user_management.models import User
from common.custom_celery_tasks import shared_dedicated_queue_retry_task


# MAX_RETRIES = 1 if settings.DEBUG else 10
logger = get_task_logger(__name__)
#
# _client: Optional[MatrixClient] = None
# client_lock = asyncio.Lock()
#
#
# async def _initialize_client():
#     global _client
#     logger.critical(f'Called initialize client')
#     async with client_lock:
#         if _client is None:
#             logger.critical(f'Initializing client')
#             _client = await MatrixClient.login_with_username_and_password(
#                 settings.MATRIX_USER_ID,
#                 settings.MATRIX_PASSWORD,
#                 "temporary-grafana-device-id",
#                 settings.MATRIX_HOMESERVER
#             )
#             logger.critical(f'==========================================\nFinished initializing client\n==========================================')
#
#
# def get_client():
#     logger.critical('Called get_client')
#     global _client
#     if _client is None:
#         logger.critical('_client is none inside get_client, starting init task')
#         asyncio.create_task(_initialize_client())
#         logger.critical('Init task created')
#     while _client is None:
#         logger.critical('Waiting on client')
#         sleep(1)
#     return _client
#

@shared_dedicated_queue_retry_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=1)
async def notify_user_via_matrix(user, alert_group, notification_policy, paging_room_id, message):
    # imported here to avoid circular import error
    from apps.base.models import UserNotificationPolicy, UserNotificationPolicyLogRecord

    logger.critical(f'DEBUGGG - inside notify_user_async')

    logger.critical(f'DEBUG - 5')
    logger.critical(f'{paging_room_id}')

    client = await MatrixClient.login_with_username_and_password(
        settings.MATRIX_USER_ID,
        settings.MATRIX_PASSWORD,
        "temporary-grafana-device-id",
        settings.MATRIX_HOMESERVER
    )

    # if not await client.is_in_room(paging_room_id):
    if not await client.is_in_room_unmodified(paging_room_id):
        # TODO - error checking is particularly important here - you can visually check that your user_id
        # exists and is correct, but you can't check that the bot's able to join a room without actually having it
        # try to do so.
        # (To be clear - what is currently here is _probably_ insufficient, but I'm reliant on the Oncall team
        # to tell me how to raise an "out-of-band" error)
        try:
            await client.join_room(paging_room_id)
        except Exception as e:
            UserNotificationPolicyLogRecord.objects.create(
                author=user,
                type=UserNotificationPolicyLogRecord.TYPE_PERSONAL_NOTIFICATION_FAILED,
                notification_policy=notification_policy,
                alert_group=alert_group,
                reason="error while sending Matrix message",
                notification_step=notification_policy.step,
                notification_channel=notification_policy.notify_by
            )
            logger.error(f"Unable to join paging_room {paging_room_id} to notify user {user.pk}:")
            logger.exception(e)
            return

    logger.critical(f'DEBUG - 6')

    await client.send_message_to_room(
        paging_room_id,
        message+' - iteration 3, with rename')
