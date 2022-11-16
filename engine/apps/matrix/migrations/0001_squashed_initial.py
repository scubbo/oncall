# TODO - other migrations file have comments suggesting that they were
# auto-generated, but I couldn't figure out how to do so - in particular,
# `engine/manage.py django makemigrations` gave `Unknown command: 'django'`,
# and `engine/manage.py makemigrations` gave a long stacktrace ending in
# `nodename nor servname provided, or not known`

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='MatrixUserIdentity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=100)),
                ('paging_room', models.CharField(max_length=100)),
            ]
        )
    ]