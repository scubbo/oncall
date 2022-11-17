from django.db import models


class MatrixUserIdentity(models.Model):
    # Django automatically inserts an auto-incrementing "id" field, so no need to specify it
    user_id = models.CharField(max_length=100)
    paging_room = models.CharField(max_length=100)

    def __str__(self):
        return self.user_id
