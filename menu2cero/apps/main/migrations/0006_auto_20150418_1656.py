# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_direccion_calle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurante',
            name='nombre',
            field=models.CharField(help_text=b'Introduzca el nombre de su restaurante.', unique=True, max_length=50),
        ),
    ]
