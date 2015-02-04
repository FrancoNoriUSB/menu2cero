# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrador',
            fields=[
                ('nombre', models.CharField(max_length=30)),
                ('correo', models.EmailField(max_length=75, serialize=False, primary_key=True)),
                ('nivel', models.DecimalField(max_digits=2, decimal_places=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Administrador',
                'verbose_name_plural': 'Administradores',
            },
            bases=(models.Model,),
        ),
    ]
