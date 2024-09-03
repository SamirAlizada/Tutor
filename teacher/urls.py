from django.urls import path, re_path
from .views import *

urlpatterns = [
    # List
    path('', daily_list, name='daily_list'),
    path('group-list/', group_list, name='group_list'),
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('pay-day/', pay_day, name='pay_day'),
    path('calendar/', calendar_view, name='calendar_view'),
    path('day/<int:year>/<int:month>/<int:day>/', day_detail, name='day_detail'),
    re_path(r'^schedule/(?P<week_offset>-?\d+)?/?$', weekly_schedule_view, name='weekly_schedule'),
    re_path(r'^week-day-detail/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<week_offset>-?\d+)/$', week_day_detail, name='week_day_detail'),
    re_path(r'^update-weekly-lesson-detail/(?P<schedule_id>\d+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<week_offset>-?\d+)/$', update_weekly_lesson_detail, name='update_weekly_lesson_detail'),
    
    # Add
    path('group/add/', add_group, name='add_group'),
    path('student/add/', add_student, name='add_student'),
    path('lesson-schedule/add/', add_lesson_schedule, name='add_lesson_schedule'),
    path('renew-student/<int:student_id>/', renew_student, name='renew_student'),

    # Update
    path('update-group/<int:pk>/', update_group, name='update_group'),
    path('lesson-schedule/update/', add_lesson_schedule, name='update_lesson_schedule'),
    path('student/update/<int:pk>/<int:group_id>/', update_student, name='update_student'),
    path('student/update/pay/<int:pk>/', update_student_pay, name='update_student_pay'),
    path('update/<int:schedule_id>/', update_lesson_schedule, name='update_lesson_schedule'),
    path('update/<int:schedule_id>/<int:year>/<int:month>/<int:day>/', update_lesson_detail, name='update_lesson_detail'),

    
    # Delete
    path('delete-group/<int:pk>/', delete_group, name='delete_group'),
    path('delete-student/<int:pk>/', delete_student, name='delete_student'),
    path('delete-student-pay/<int:pk>/', delete_student_pay, name='delete_student_pay'),
    path('delete/<int:schedule_id>/<int:year>/<int:month>/<int:day>/', delete_lesson_detail, name='delete_lesson_detail'),
    path('delete/<int:schedule_id>/', delete_lesson_schedule, name='delete_lesson_schedule'),

    # Account
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('pdf-daily/', generate_pdf_daily, name='pdf_daily'),
    path('pdf-calendar/', generate_pdf_calendar, name='pdf_calendar'),
    path('pdf-weekly-schedule/', generate_pdf_weekly, name='pdf_weekly_schedule'),

    
    

]
