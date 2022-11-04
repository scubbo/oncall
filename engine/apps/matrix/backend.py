from apps.base.messaging import BaseMessagingBackend
from apps.matrix.tasks import notify_user_async


class MatrixBackend(BaseMessagingBackend):
    backend_id = "MATRIX"
    label = "Matrix"  # TODO - it'd be cool to add an icon of the Matrix logo here!
    short_label = "Matrix"
    available_for_use = True

    # TODO - change these to appropriate values once you actually have messages showing up!
    templater = "apps.email.alert_rendering.AlertEmailTemplater"
    template_fields = ("title", "message")

    def serialize_user(self, user):
        # TODO: This appears to be used in serializing a representation of how to contact the user via
        # this given backend (see usage in `engine/apps/api/serializers/user.py:get_messaging_backends`,
        # and implementation in `engine/apps/email/backend.py`).
        #
        # I'm not messing with this just yet, since messing with the `user` class to add a new "matrixHandle"
        # property seems like a bigger change than I should make before actually talking to an Oncall dev!
        return {"matrix_handle": f"DEBUG this _would_ be their handle, but now it's just their name: {user.name}"}

    def notify_user(self, user, alert_group, notification_policy):
        notify_user_async.delay(
            user_pk=user.pk, alert_group_pk=alert_group.pk, notification_policy_pk=notification_policy.pk
        )
