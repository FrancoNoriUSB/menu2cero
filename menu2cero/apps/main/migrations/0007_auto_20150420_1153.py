# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150418_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='red_social',
            name='facebook',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='red_social',
            name='instagram',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='red_social',
            name='twitter',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
