# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(unique=True, max_length=30)),
                ('imagen', models.ImageField(upload_to=b'uploads/img/categorias')),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Categor\xeda',
                'verbose_name_plural': 'Categor\xedas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Ciudad',
                'verbose_name_plural': 'Ciudades',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cargo', models.CharField(max_length=20, choices=[(b'', b'- Cargo -'), (b'Gerente', b'Gerente'), (b'Encargado', b'Encargado'), ('Due\xf1o', 'Due\xf1o')])),
                ('telefono', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('user',),
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comensal',
            fields=[
                ('ip', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('status', models.CharField(max_length=20, null=True)),
            ],
            options={
                'ordering': ('ip',),
                'verbose_name': 'Comensal',
                'verbose_name_plural': 'Comensales',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coord', models.CharField(max_length=50)),
                ('direccion', models.CharField(max_length=100)),
                ('ciudad', models.ForeignKey(to='main.Ciudad')),
            ],
            options={
                'ordering': ('ciudad',),
                'verbose_name': 'Direcci\xf3n',
                'verbose_name_plural': 'Direcciones',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Horario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia', models.CharField(max_length=10)),
                ('desde', models.CharField(max_length=20)),
                ('hasta', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('restaurante',),
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imagen', models.ImageField(upload_to=b'uploads/img/rest/')),
                ('thumbnail', models.ImageField(null=True, upload_to=b'uploads/img/rest/thumbnails/', blank=True)),
                ('descripcion', models.CharField(max_length=140, null=True)),
            ],
            options={
                'ordering': ('imagen',),
                'verbose_name': 'Im\xe1gen',
                'verbose_name_plural': 'Im\xe1genes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ('restaurante',),
                'verbose_name': 'Men\xfa',
                'verbose_name_plural': 'Men\xfas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metodo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=12, choices=[(b'Efectivo', b'Efectivo'), (b'Debito', 'D\xe9bito'), (b'Credito', 'Cr\xe9dito'), (b'Cesta Ticket', b'Cesta Ticket')])),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'M\xe9todo',
                'verbose_name_plural': 'M\xe9todos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('monto', models.DecimalField(max_digits=10, decimal_places=2)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('vigencia', models.DateField()),
                ('tipo', models.CharField(max_length=3, choices=[(b'mensual', b'mensual'), (b'trimestral', b'trimestral'), (b'semanal', b'semestral'), (b'anual', b'anual')])),
                ('numero', models.DecimalField(max_digits=20, decimal_places=2)),
                ('cliente', models.ForeignKey(to='main.Cliente')),
            ],
            options={
                'ordering': ('fecha',),
                'verbose_name': 'Pago',
                'verbose_name_plural': 'Pagos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=30)),
                ('descripcion', models.CharField(max_length=300)),
                ('max_imagenes', models.IntegerField(max_length=3)),
                ('estadisticas', models.BooleanField(default=False)),
                ('posicionamiento', models.CharField(default=b'N/A', max_length=10, choices=[(b'Bajo', b'Bajo'), (b'Medio', b'Medio'), (b'Alto', b'Alto')])),
                ('boletin', models.BooleanField(default=False)),
                ('impresion', models.BooleanField(default=False)),
                ('costo', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Plan',
                'verbose_name_plural': 'Planes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=30)),
                ('descripcion', models.CharField(max_length=300)),
                ('precio', models.DecimalField(max_digits=10, decimal_places=2)),
                ('disponibilidad', models.BooleanField(default=True, help_text=b'Desmarque si el plato no se encuentra disponible')),
                ('imagen', models.ImageField(default=b'', upload_to=b'uploads/img/menus/')),
                ('menu', models.ForeignKey(to='main.Menu')),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Plato',
                'verbose_name_plural': 'Platos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Red_social',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('facebook', models.CharField(max_length=100, null=True)),
                ('twitter', models.CharField(max_length=50, null=True)),
                ('instagram', models.CharField(max_length=50, null=True)),
            ],
            options={
                'ordering': ('facebook',),
                'verbose_name': 'Red_social',
                'verbose_name_plural': 'Redes_sociales',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Restaurante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rif', models.CharField(max_length=13)),
                ('nombre', models.CharField(help_text=b'Introduzca el nombre de su restaurante.', max_length=50)),
                ('logo', models.ImageField(default=b'uploads/img/logos/ico.png', upload_to=b'uploads/img/logos/')),
                ('descripcion', models.TextField(max_length=300)),
                ('status', models.CharField(default=b'Activo', max_length=20, editable=False, choices=[(b'Activo', b'Activo'), (b'Inactivo', b'Inactivo'), (b'Eliminado', b'Eliminado')])),
                ('tipo', models.CharField(max_length=4, choices=[(b'Restaurante', b'Restaurante'), (b'Bar', b'Bar'), ('Helader\xeda', 'Helader\xeda'), (b'Panader\xc3\xada', 'Panader\xeda'), ('caf\xe9', b'Cafeter\xc3\xada')])),
                ('abierto', models.BooleanField(default=True, help_text=b'Desmarcar si su restaurante se encuentra cerrado')),
                ('visibilidad', models.CharField(max_length=10, null=True, choices=[('P\xfablico', b'P\xc3\xbablico'), (b'Privado', b'Privado')])),
                ('categoria', models.ManyToManyField(to='main.Categoria')),
                ('cliente', models.ForeignKey(to='main.Cliente')),
                ('metodos_pago', models.ManyToManyField(to='main.Metodo')),
                ('plan', models.ForeignKey(to='main.Plan')),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Restaurante',
                'verbose_name_plural': 'Restaurantes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Servicio',
                'verbose_name_plural': 'Servicios',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TelefonoRestaurante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.CharField(max_length=20)),
                ('display', models.BooleanField(default=True, help_text=b'Marcado si desea que se muestre en el perfil')),
                ('restaurante', models.ForeignKey(related_name='telefonos', to='main.Restaurante')),
            ],
            options={
                'ordering': ('numero',),
                'abstract': False,
                'verbose_name': 'Tel\xe9fono',
                'verbose_name_plural': 'Tel\xe9fonos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Tipo',
                'verbose_name_plural': 'Tipos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('nombre', models.CharField(max_length=40)),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valor', models.DecimalField(max_digits=2, decimal_places=1)),
                ('restaurante', models.ForeignKey(to='main.Restaurante')),
            ],
            options={
                'verbose_name': 'Voto',
                'verbose_name_plural': 'Votos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zona',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('ciudad', models.ForeignKey(to='main.Ciudad')),
            ],
            options={
                'ordering': ('nombre',),
                'verbose_name': 'Zona',
                'verbose_name_plural': 'Zonas',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='restaurante',
            name='servicios',
            field=models.ManyToManyField(to='main.Servicio'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='red_social',
            name='restaurante',
            field=models.OneToOneField(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='plato',
            name='tipo',
            field=models.ForeignKey(to='main.Tipo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pago',
            name='restaurante',
            field=models.ForeignKey(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='menu',
            name='restaurante',
            field=models.ForeignKey(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imagen',
            name='restaurante',
            field=models.ForeignKey(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='horario',
            name='restaurante',
            field=models.ForeignKey(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='direccion',
            name='restaurante',
            field=models.OneToOneField(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='direccion',
            name='zona',
            field=models.ForeignKey(to='main.Zona'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comensal',
            name='restaurante',
            field=models.ManyToManyField(to='main.Restaurante'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cliente',
            name='user',
            field=models.OneToOneField(to='main.User'),
            preserve_default=True,
        ),
    ]
