# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voto',
            name='restaurante',
        ),
        migrations.AddField(
            model_name='restaurante',
            name='votos',
            field=models.ManyToManyField(to='main.Voto'),
            preserve_default=True,
        ),
    ]
