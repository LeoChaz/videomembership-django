# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 10:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0015_auto_20160310_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 17, 10, 40, 32, 188438, tzinfo=utc)),
        ),
    ]
