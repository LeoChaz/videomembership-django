# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-10 17:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0014_auto_20160309_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 10, 17, 27, 58, 226765, tzinfo=utc)),
        ),
    ]
