import logging

from django.db import models


class AllMatrixUserIdentityManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        return super().get_queryset()


class MatrixUserIdentityManager(models.Manager):
    use_in_migrations = False

    def get_queryset(self):
        return super().get_queryset().filter(counter=1)

    def get(self, **kwargs):
        try:
            instance = super().get(**kwargs, is_restricted=False, is_ultra_restricted=False)
        except MatrixUserIdentity.DoesNotExist:
            instance = self.filter(**kwargs).first()
            if instance is None:
                raise MatrixUserIdentity.DoesNotExist
        return instance


class MatrixUserIdentity(models.Model):

    objects = MatrixUserIdentityManager()
    all_objects = AllMatrixUserIdentityManager()

    id = models.AutoField(primary_key=True)

    matrix_user_id = models.CharField(max_length=100)

    def __str__(self):
        return self.matrix_user_id
