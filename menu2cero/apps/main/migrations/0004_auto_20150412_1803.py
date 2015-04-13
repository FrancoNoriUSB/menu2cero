# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150408_2147'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='direccion',
            name='coord',
        ),
        migrations.AddField(
            model_name='direccion',
            name='latitud',
            field=models.DecimalField(default=10.4683918, max_digits=20, decimal_places=17),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='direccion',
            name='longitud',
            field=models.DecimalField(default=-66.8903658, max_digits=20, decimal_places=17),
            preserve_default=False,
        ),
    ]
