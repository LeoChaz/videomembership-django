# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-17 10:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0007_auto_20160310_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='date_end',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 17, 10, 40, 32, 176865, tzinfo=utc), verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 17, 10, 40, 32, 176794, tzinfo=utc), verbose_name='Start Date'),
        ),
    ]
