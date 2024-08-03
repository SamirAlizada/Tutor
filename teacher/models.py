from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import datetime

class Group(models.Model):
    name = models.CharField(max_length=39)

    def __str__(self):
        return self.name

class LessonSchedule(models.Model):
    group = models.ForeignKey(Group, related_name='schedules', on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True)
    time = models.TimeField(default=datetime.time(12, 0))

    DAYS_OF_WEEK = (
        ('Bazar Ertəsi', 'Bazar Ertəsi'),
        ('Çərşənbə Axşamı', 'Çərşənbə Axşamı'),
        ('Çərşənbə', 'Çərşənbə'),
        ('Cümə Axşamı', 'Cümə Axşamı'),
        ('Cümə', 'Cümə'),
        ('Şənbə', 'Şənbə'),
        ('Bazar', 'Bazar'),
    )
    day_of_week = models.CharField(max_length=30, choices=DAYS_OF_WEEK, null=True)

class Student(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    price = models.IntegerField()
    grade = models.IntegerField()
    add_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    student_mobile = models.CharField(max_length=15, null=True, blank=True)
    parent_mobile = models.CharField(max_length=15, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.add_date + relativedelta(months=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
