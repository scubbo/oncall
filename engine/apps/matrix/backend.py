from apps.base.messaging import BaseMessagingBackend
from apps.matrix.tasks import notify_user_via_celery


class MatrixBackend(BaseMessagingBackend):
    backend_id = "MATRIX"
    label = "Matrix"  # TODO - it'd be cool to add an icon of the Matrix logo here!
    short_label = "Matrix"
    available_for_use = True

    # TODO - change these to appropriate values once they're understood
    templater = "apps.email.alert_rendering.AlertEmailTemplater"
    template_fields = ("title", "message")

    def serialize_user(self, user):
        return {"matrix_user_id": user.matrix_user_identity}

    def notify_user(self, user, alert_group, notification_policy):
        notify_user_via_celery.delay(
            user_pk=user.pk, alert_group_pk=alert_group.pk, notification_policy_pk=notification_policy.pk
        )
