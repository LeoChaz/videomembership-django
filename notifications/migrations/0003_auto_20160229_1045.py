# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-29 10:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20160226_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action_object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='target_object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
