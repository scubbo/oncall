from apps.base.messaging import BaseMessagingBackend
from apps.matrix.tasks import notify_user_via_celery
from django.conf import settings
from apps.matrix.alert_rendering import build_message

import asyncio

from apps.user_management.models import User

from nio import AsyncClient, LoginResponse
from .client import MatrixClient

import logging
logger = logging.getLogger(__name__)


class MatrixBackend(BaseMessagingBackend):
    backend_id = "MATRIX"
    label = "Matrix"  # TODO - it'd be cool to add an icon of the Matrix logo here!
    short_label = "Matrix"
    available_for_use = True

    # TODO - change these to appropriate values once they're understood
    templater = "apps.email.alert_rendering.AlertEmailTemplater"
    template_fields = ("title", "message")

    def serialize_user(self, user):
        return {key: repr(getattr(user, key)) for key in ['user_id', 'name', 'matrix_user_identity']}

    def notify_user(self, user, alert_group, notification_policy):
        logger.critical('DEBUG - 0')
        # notify_user_via_celery(
        #     user_pk=user.pk, alert_group_pk=alert_group.pk, notification_policy_pk=notification_policy.pk
        # )
        from apps.base.models import UserNotificationPolicy, UserNotificationPolicyLogRecord

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

        paging_room_id = user.matrix_user_identity.paging_room_id
        message = build_message(alert_group, user.matrix_user_identity)
        asyncio.run(self.debugging_method(user, alert_group, notification_policy, paging_room_id, message))

    async def debugging_method(self, user, alert_group, notification_policy, paging_room_id, message):
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
        logger.critical(client)

        # if not await client.is_in_room(paging_room_id):
        if not await client.is_in_room_unmodified(paging_room_id):
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
            message)
