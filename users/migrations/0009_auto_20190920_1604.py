# Generated by Django 2.0.6 on 2019-09-20 10:34

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190809_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdetails',
            name='gender',
            field=models.IntegerField(default=users.models.gender),
        ),
    ]