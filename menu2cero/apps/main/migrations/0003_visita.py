# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150502_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visita',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cantidad', models.IntegerField(max_length=20)),
                ('ip', models.CharField(max_length=40)),
            ],
            options={
                'ordering': ('ip',),
                'verbose_name': 'Visita',
                'verbose_name_plural': 'Visitas',
            },
            bases=(models.Model,),
        ),
    ]
