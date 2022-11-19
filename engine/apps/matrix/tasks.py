import asyncio

from celery.utils.log import get_task_logger
from django.conf import settings

from apps.alerts.models import AlertGroup
from apps.matrix.alert_rendering import build_message
from apps.matrix.client import MatrixClient
from apps.matrix.models import MatrixUserIdentity
from apps.user_management.models import User
from common.custom_celery_tasks import shared_dedicated_queue_retry_task


MAX_RETRIES = 1 if settings.DEBUG else 10
logger = get_task_logger(__name__)

# TODO - make this a singleton!
client = MatrixClient.login_with_username_and_password(
    settings.MATRIX_USER_ID,
    settings.MATRIX_PASSWORD,
    "temporary-grafana-device-id",
    settings.MATRIX_HOMESERVER
)


@shared_dedicated_queue_retry_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=MAX_RETRIES)
def notify_user_via_celery(user_pk, alert_group_pk, notification_policy_pk):
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
        logger.error(f"Error while sending Matrix message - no matrix_user_identity for user {user.pk}")
        return

    # Unfortunately, interaction with Matrix via nio is predominantly via async functions,
    # and it turns out that multiple nested calls to `asyncio.get_event_loop().run_until_complete(`
    # can cause calls to hang, so we partition the logic off in a single async function wherein
    # `await` can be used instead.
    #
    # (Conversely, calls to, e.g., `User.objects.get` can only be called from a synchronous context,
    # hence why we can't move _all_ the logic into a single async function)
    event_loop = asyncio.get_event_loop()
    logger.critical(f'{event_loop=}')
    logger.critical(f'{event_loop.is_running()=}')
    asyncio.get_event_loop().run_until_complete(notify_user_async(user, alert_group, notification_policy))


async def notify_user_async(user, alert_group, notification_policy):
    # imported here to avoid circular import error
    from apps.base.models import UserNotificationPolicy, UserNotificationPolicyLogRecord

    logger.critical(f'DEBUGGG - inside notify_user_async')
    logger.critical(f'{asyncio.get_event_loop().is_running()}')

    identity = user.matrix_user_identity
    paging_room_id = identity.paging_room_id

    logger.critical(f'DEBUG - 5')
    logger.critical(f'{paging_room_id}')

    if not await client.is_in_room(paging_room_id):
        # TODO - error checking is particularly important here - you can visually check that your user_id
        # exists and is correct, but you can't check that the bot's able to join a room without actually having it
        # try to do so.
        # (To be clear - what is currently here is _probably_ insufficient, but I'm reliant on the Oncall team
        # to tell me how to raise an "out-of-band" error)
        logger.critical(f'DEBUG - trying to join room')
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
        build_message(alert_group, identity.user_id))
