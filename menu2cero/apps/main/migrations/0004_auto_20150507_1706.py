# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_visita'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plato',
            name='imagen',
            field=models.ImageField(default=b'', null=True, upload_to=b'uploads/img/menus/'),
        ),
    ]
