# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150420_1153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagen',
            options={'ordering': ('descripcion',), 'verbose_name': 'Im\xe1gen', 'verbose_name_plural': 'Im\xe1genes'},
        ),
        migrations.RenameField(
            model_name='imagen',
            old_name='imagen',
            new_name='archivo',
        ),
    ]
