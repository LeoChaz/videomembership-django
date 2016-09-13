# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 14:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_auto_20160308_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='date_end',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 9, 14, 12, 25, 480859, tzinfo=utc), verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='date_start',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 9, 14, 12, 25, 480805, tzinfo=utc), verbose_name='Start Date'),
        ),
    ]