# Generated by Django 4.2.4 on 2023-08-26 19:04

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gov_body_user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('LOCAL', 'Local'), ('DISTRICT', 'District'), ('STATE', 'State')], max_length=20)),
                ('email', models.EmailField(error_messages={'unique': 'A user with the same email already exists.'}, max_length=254, unique=True)),
                ('gov_body_name', models.CharField(max_length=50)),
                ('contact_number', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('land_number', models.AutoField(primary_key=True, serialize=False)),
                ('locality', models.CharField(max_length=50)),
                ('district', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('active_from', models.DateField(auto_now_add=True)),
                ('active_till', models.DateField(blank=True, default=None, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('parent_land_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.land')),
            ],
        ),
        migrations.CreateModel(
            name='LandOwnershipRegistry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_date', models.DateField(auto_now_add=True)),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.land')),
            ],
        ),
        migrations.CreateModel(
            name='NormalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('adhar_id', models.CharField(max_length=10, unique=True)),
                ('contact_number', models.CharField(max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='TaxInvoice',
            fields=[
                ('tax_invoice_id', models.AutoField(primary_key=True, serialize=False)),
                ('area', models.IntegerField()),
                ('amount', models.IntegerField()),
                ('tax_date', models.DateField(auto_now_add=True)),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.land')),
                ('registry_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.landownershipregistry')),
            ],
        ),
        migrations.CreateModel(
            name='TaxInvoicePayment',
            fields=[
                ('tax_payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('payed_amount', models.IntegerField()),
                ('payment_date', models.DateField(auto_now_add=True)),
                ('tax_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.taxinvoice')),
            ],
        ),
        migrations.AddField(
            model_name='landownershipregistry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.normaluser'),
        ),
        migrations.CreateModel(
            name='LandGeography',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('land_type', models.CharField(choices=[('RESIDENTIAL', 'Residential'), ('AGRICULTURAL', 'Agricultural'), ('COMMERCIAL', 'Commercial'), ('INDUSTRIAL', 'Industrial'), ('TRANSPORT', 'Transport'), ('RECREATIONAL', 'Recreational'), ('INVESTMENT', 'Investment'), ('ECOSENSITIVE', 'Ecosensitive'), ('FOREST', 'Forest'), ('WET', 'Wet'), ('RANGE', 'Range'), ('BARREN', 'Barren')], max_length=20)),
                ('location_coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('boundary_polygon', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('area', models.IntegerField()),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.land')),
            ],
        ),
        migrations.AddField(
            model_name='land',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.normaluser'),
        ),
        migrations.CreateModel(
            name='Gov_body_Address',
            fields=[
                ('address_id', models.AutoField(primary_key=True, serialize=False)),
                ('locality', models.CharField(max_length=20)),
                ('district', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=20)),
                ('country', models.CharField(default='INDIA', max_length=20)),
                ('gov_body', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.gov_body_user')),
            ],
        ),
    ]