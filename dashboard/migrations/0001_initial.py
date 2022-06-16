# Generated by Django 4.0.5 on 2022-06-15 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='selector_Options',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('label', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='seoul_bike_2021',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('weekday', models.IntegerField()),
                ('by_id', models.IntegerField()),
                ('st_id1', models.IntegerField(db_index=True)),
                ('st_id2', models.IntegerField(db_index=True)),
                ('riding_time', models.IntegerField()),
                ('dist', models.FloatField()),
                ('m_pm', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='station_near_subway',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bi_st_id', models.IntegerField()),
                ('sub_st_id', models.IntegerField(null=True)),
                ('sub_name', models.CharField(max_length=20, null=True)),
                ('sub_line', models.CharField(max_length=10, null=True)),
                ('sub_long', models.FloatField(null=True)),
                ('sub_lat', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='stationInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('st_id', models.IntegerField(db_index=True)),
                ('st_name', models.CharField(max_length=40)),
                ('district', models.CharField(max_length=10)),
                ('latitude', models.FloatField()),
                ('longtitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WiseSaying',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
    ]
