# Generated by Django 4.1.2 on 2024-07-28 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0009_alter_group_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=39),
        ),
    ]
