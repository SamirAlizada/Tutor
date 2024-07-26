from django.contrib import admin
from .models import Group, Student, LessonSchedule

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'group', 'price', 'grade', 'add_date', 'end_date')
    list_filter = ('group', 'add_date')
    search_fields = ('full_name',)

@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'start_date', 'end_date', 'day_of_week')
    search_fields = ('group', 'start_date', 'end_date', 'day_of_week')