# Generated by Django 4.1.2 on 2024-09-03 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0017_alter_student_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='full_name',
            field=models.CharField(max_length=38),
        ),
    ]
