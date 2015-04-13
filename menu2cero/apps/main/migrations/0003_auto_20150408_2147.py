# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150408_2028'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='voto',
            options={'ordering': ('id',), 'verbose_name': 'Voto', 'verbose_name_plural': 'Votos'},
        ),
        migrations.RemoveField(
            model_name='restaurante',
            name='tipo',
        ),
    ]
