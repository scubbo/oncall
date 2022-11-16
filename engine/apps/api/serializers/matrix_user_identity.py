from rest_framework import serializers

from apps.matrix.models import MatrixUserIdentity


class MatrixUserIdentitySerializer(serializers.ModelSerializer):
    pk = serializers.CharField(read_only=True, source="public_primary_key")
    user_id = serializers.CharField()
    paging_room = serializers.CharField()

    class Meta:
        model = MatrixUserIdentity
        fields = ["pk", "user_id", "paging_room"]
