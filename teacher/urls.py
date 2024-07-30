from django.urls import path
from .views import *

urlpatterns = [
    path('', daily_list, name='daily_list'),
    path('group_list/', group_list, name='group_list'),
    path('group/add/', add_group, name='add_group'),
    path('lesson-schedule/add/', add_lesson_schedule, name='add_lesson_schedule'),
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('student/add/', add_student, name='add_student'),

    # Update
    path('update-group/<int:pk>/', update_group, name='update_group'),
    path('lesson-schedule/update/', add_lesson_schedule, name='update_lesson_schedule'),
    path('student/update/<int:pk>/<int:group_id>/', update_student, name='update_student'),
    path('student/update/pay/<int:pk>/', update_student_pay, name='update_student_pay'),

    # Delete
    path('delete-group/<int:pk>/', delete_group, name='delete_group'),
    path('delete-student/<int:pk>/', delete_student, name='delete_student'),

    path('pay-day/', pay_day, name='pay_day'),
    path('calendar/', calendar_view, name='calendar_view'),

    path('day/<int:year>/<int:month>/<int:day>/', day_detail, name='day_detail'),


    path('renew-student/<int:student_id>/', renew_student, name='renew_student'),

    path('update/<int:schedule_id>/', update_lesson_schedule, name='update_lesson_schedule'),
    # path('delete/<int:schedule_id>/<int:year>/<int:month>/<int:day>/', delete_lesson_schedule, name='delete_lesson_schedule'),
    path('delete/<int:schedule_id>/', delete_lesson_schedule, name='delete_lesson_schedule'),


    # Account
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
