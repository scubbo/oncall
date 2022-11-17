from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.api.permissions import MODIFY_ACTIONS, READ_ACTIONS, ActionPermission, AnyRole, IsAdmin
from apps.api.serializers.matrix_user_identity import MatrixUserIdentitySerializer
from apps.auth_token.auth import PluginAuthentication
from common.api_helpers.mixins import PublicPrimaryKeyMixin
from common.insight_log import EntityEvent, write_resource_insight_log

import logging
logger = logging.getLogger(__name__)


class MatrixUserIdentityView(
    PublicPrimaryKeyMixin,
    viewsets.ModelViewSet
):
    authentication_classes = (PluginAuthentication,)
    permission_classes = (IsAuthenticated, ActionPermission)

    action_permissions = {
        IsAdmin: (*MODIFY_ACTIONS, "set_default"),
        AnyRole: READ_ACTIONS,
    }

    serializer_class = MatrixUserIdentitySerializer

    def perform_create(self, serializer):
        logger.fatal(f'DEBUG - perform_create called with {serializer=}, {self.request=}')
        serializer.save()
        write_resource_insight_log(
            instance=serializer.instance,
            author=self.request.user,
            event=EntityEvent.CREATED,
        )
