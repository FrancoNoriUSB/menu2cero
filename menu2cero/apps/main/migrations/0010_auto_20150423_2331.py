# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurante',
            name='slug',
            field=models.SlugField(default=' ', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='plato',
            name='imagen',
            field=models.ImageField(default=b'', upload_to=b'uploads/img/menus/'),
        ),
        migrations.AlterField(
            model_name='restaurante',
            name='nombre',
            field=models.CharField(help_text=b'Introduzca el nombre de su restaurante.', unique=True, max_length=100),
        ),
    ]
