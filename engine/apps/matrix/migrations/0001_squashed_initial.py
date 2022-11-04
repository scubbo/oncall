# Generated by Django 3.2.16 on 2022-11-19 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='MatrixUserIdentity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('paging_room_id', models.CharField(blank=True, max_length=100, null=True)),
            ]
        )
    ]