# Generated by Django 3.1.5 on 2021-01-19 03:23

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BuyList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('firstname', models.CharField(max_length=250)),
                ('plz', models.CharField(max_length=250)),
                ('City', models.CharField(max_length=250)),
                ('Street', models.CharField(max_length=250)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('session_id', models.CharField(max_length=250, unique=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(help_text='Contact phone number', max_length=128, region=None, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(auto_now_add=True)),
                ('last_active', models.DateTimeField(auto_now_add=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('usertype', models.CharField(choices=[('HF', 'Helfer'), ('HFS', 'HilfeSuchender')], default='Helfer', max_length=50)),
                ('password', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payed', models.BooleanField(default=False)),
                ('done', models.BooleanField(default=False)),
                ('raiting', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)])),
                ('finished_date', models.DateTimeField(null=True)),
                ('buylist', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pages.buylist')),
                ('helper', models.ForeignKey(limit_choices_to={'usertype': 'HF'}, on_delete=django.db.models.deletion.CASCADE, related_name='helper_requests_created', to='pages.user')),
                ('helpsearcher', models.ForeignKey(limit_choices_to={'usertype': 'HFS'}, on_delete=django.db.models.deletion.CASCADE, related_name='helpseacher_requests_created', to='pages.user')),
            ],
        ),
        migrations.AddField(
            model_name='buylist',
            name='helpsearcher',
            field=models.ForeignKey(limit_choices_to={'usertype': 'HFS'}, on_delete=django.db.models.deletion.CASCADE, to='pages.user'),
        ),
        migrations.AddField(
            model_name='buylist',
            name='items',
            field=models.ManyToManyField(to='pages.Item'),
        ),
    ]
