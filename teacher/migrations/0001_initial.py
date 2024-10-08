# Generated by Django 4.1.2 on 2024-07-23 10:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('time', models.TimeField(null=True)),
                ('day_of_week', models.PositiveSmallIntegerField(choices=[(2, 'Bazar Ertəsi'), (3, 'Çərşənbə Axşamı'), (4, 'Çərşənbə'), (5, 'Cümə Axşamı'), (6, 'Cümə'), (7, 'Şənbə'), (1, 'Bazar')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('grade', models.IntegerField()),
                ('add_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacher.group')),
            ],
        ),
    ]
