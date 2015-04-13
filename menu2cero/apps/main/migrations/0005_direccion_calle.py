# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150412_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='direccion',
            name='calle',
            field=models.CharField(default='calle o avenida', max_length=100),
            preserve_default=False,
        ),
    ]
