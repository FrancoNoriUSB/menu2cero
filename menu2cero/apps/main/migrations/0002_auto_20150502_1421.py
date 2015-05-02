# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='imagen',
            field=models.ImageField(null=True, upload_to=b'uploads/img/servicios'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='servicio',
            name='imagen_gris',
            field=models.ImageField(null=True, upload_to=b'uploads/img/servicios/grises'),
            preserve_default=True,
        ),
    ]
