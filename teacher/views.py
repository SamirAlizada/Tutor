from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.forms import formset_factory
from calendar import Calendar, monthrange
from django.template.loader import render_to_string
from .models import Group, Student, LessonSchedule
from .forms import GroupForm, StudentForm, LessonScheduleForm
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from .forms import LessonScheduleForm
import datetime
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
import pdfkit

#Add
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'group/add_group.html', {'form': form})

def add_lesson_schedule(request):
    LessonScheduleFormSet = formset_factory(LessonScheduleForm, extra=1)
    
    groups = Group.objects.all()  # Define the groups variable here

    if request.method == 'POST':
        formset = LessonScheduleFormSet(request.POST)
        group_id = request.POST.get('group')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        if not group_id:
            messages.error(request, "Qrup seçilmədi. Zəhmət olmasa qrup seçin.")
            return render(request, 'lessonSchedule/add_lesson_schedule.html', {
                'formset': formset,
                'groups': groups,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'group_id': group_id
            })

        group = Group.objects.get(id=group_id)

        try:
            # Parse start_date
            start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, "Başlama tarixinin formatı yanlışdır.")
            return render(request, 'lessonSchedule/add_lesson_schedule.html', {
                'formset': formset,
                'groups': groups,
                'start_date': start_date_str,
                'end_date': end_date_str,
                'group_id': group_id
            })

        # Set end_date to start_date if not provided
        end_date = datetime.datetime.strptime(end_date_str, '%d/%m/%Y').date() if end_date_str else start_date

        if formset.is_valid():
            for form in formset:
                day_of_week = form.cleaned_data.get('day_of_week')
                time = form.cleaned_data.get('time', datetime.time(12, 0))  # Use 12:00 as default value

                # Ensure time is provided
                if not time:
                    continue

                # Defining days as a number (Monday=0, Sunday=6)
                days = {
                    'Bazar Ertəsi': 0,    # Monday
                    'Çərşənbə Axşamı': 1, # Tuesday
                    'Çərşənbə': 2,        # Wednesday
                    'Cümə Axşamı': 3,    # Thursday
                    'Cümə': 4,           # Friday
                    'Şənbə': 5,          # Saturday
                    'Bazar': 6           # Sunday
                }

                if not day_of_week:
                    # Determine the day_of_week based on start_date
                    day_of_week_number = start_date.weekday()
                    day_of_week = next((day for day, number in days.items() if number == day_of_week_number), None)
                else:
                    day_of_week_number = days.get(day_of_week)
                    if day_of_week_number is None:
                        continue  # Skip if day_of_week is invalid

                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() == day_of_week_number:
                        try:
                            LessonSchedule.objects.create(
                                group=group,
                                start_date=current_date,
                                end_date=current_date,
                                time=time,
                                day_of_week=day_of_week
                            )
                        except Exception as e:
                            print(f"Error creating LessonSchedule: {e}")
                    current_date += timedelta(days=1)

            messages.success(request, "Təqvimə uğurla əlavə edildi.")
            return redirect('add_lesson_schedule')
        else:
            for form in formset:
                print(form.errors)  # Print form errors for debugging
            messages.error(request, "Formda səhvlər var. Zəhmət olmasa yoxlayın.")
    else:
        formset = LessonScheduleFormSet()

    # If the request method is GET or there's an error, return the form with any previously entered data
    return render(request, 'lessonSchedule/add_lesson_schedule.html', {
        'formset': formset,
        'groups': groups,
        'start_date': request.POST.get('start_date', ''),
        'end_date': request.POST.get('end_date', ''),
        'group_id': request.POST.get('group', '')
    })

def add_student(request):
    if request.method == 'POST':
        print("POST request received")
        form = StudentForm(request.POST)
        if form.is_valid():
            print("Form düzgündür")
            form.save()
            messages.success(request, 'Tələbə uğurla əlavə edildi.')
            return redirect('add_student') 
        else:
            print("Form düzgün deyil")
            print(form.errors)
    else:
        form = StudentForm()
    return render(request, 'student/add_student.html', {'form': form})

# Update
def update_student_pay(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            # Update end_date if add_date changes
            if student.add_date != student.__class__.objects.get(pk=pk).add_date:
                student.end_date = student.add_date + relativedelta(months=1)
            student.save()
            return redirect('pay_day')
    else:
        form = StudentForm(instance=student)
    return render(request, 'student/update_student_pay.html', {'form': form})

def update_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    form = GroupForm(instance=group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    return render(request, 'group/update_group.html', {'form': form})

def update_student(request, pk, group_id):
    student = get_object_or_404(Student, pk=pk)
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            # Update end_date if add_date changes
            if student.add_date != student.__class__.objects.get(pk=pk).add_date:
                student.end_date = student.add_date + relativedelta(months=1)
            student.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'student/update_student.html', {'form': form, 'group': group})

def update_lesson_schedule(request, schedule_id):
    lesson_schedule = get_object_or_404(LessonSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = LessonScheduleForm(request.POST, instance=lesson_schedule)
        group_id = request.POST.get('group')
        group = get_object_or_404(Group, id=group_id)
        
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, "Start date format is incorrect.")
            return render(request, 'lessonSchedule/update_lesson_schedule.html', {
                'form': form,
                'lesson_schedule': lesson_schedule,
                'groups': Group.objects.all(),
                'next_url': request.GET.get('next', ''),
                'schedule_id' : request.GET.get('schedule_id', ''),
                'selected_year': request.GET.get('year', ''),
                'selected_month': request.GET.get('month', ''),
                'selected_day': request.GET.get('day', ''),
                'year': request.GET.get('year', ''),
                'month': request.GET.get('month', ''),
                'day': request.GET.get('day', ''),
            })

        end_date = datetime.datetime.strptime(end_date_str, '%d/%m/%Y').date() if end_date_str else start_date

        if form.is_valid():
            lesson_schedule.group = group
            lesson_schedule.start_date = start_date
            lesson_schedule.end_date = end_date
            lesson_schedule.time = form.cleaned_data.get('time', datetime.time(12, 0))
            lesson_schedule.day_of_week = form.cleaned_data.get('day_of_week')
            lesson_schedule.save()
            return redirect('daily_list')
        else:
            messages.error(request, "There are errors in the form. Please check.")
    else:
        form = LessonScheduleForm(instance=lesson_schedule)

    return render(request, 'lessonSchedule/update_lesson_schedule.html', {
        'form': form,
        'lesson_schedule': lesson_schedule,
        'groups': Group.objects.all(),
        'next_url': request.GET.get('next', ''),
        'schedule_id' : request.GET.get('schedule_id', ''),
        'selected_year': request.GET.get('year', ''),
        'selected_month': request.GET.get('month', ''),
        'selected_day': request.GET.get('day', ''),
        'year': request.GET.get('year', ''),
        'month': request.GET.get('month', ''),
        'day': request.GET.get('day', ''),
    })

def update_lesson_detail(request, schedule_id, year, month, day):
    lesson_schedule = get_object_or_404(LessonSchedule, id=schedule_id)
    if request.method == 'POST':
        form = LessonScheduleForm(request.POST, instance=lesson_schedule)
        group_id = request.POST.get('group')
        group = Group.objects.get(id=group_id)
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        try:
            # Parse start_date
            start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, "Start date format is incorrect.")
            return redirect('update_lesson_schedule', id=schedule_id)

        # Set end_date to start_date if not provided
        end_date = datetime.datetime.strptime(end_date_str, '%d/%m/%Y').date() if end_date_str else start_date

        if form.is_valid():
            lesson_schedule.group = group
            lesson_schedule.start_date = start_date
            lesson_schedule.end_date = end_date
            lesson_schedule.time = form.cleaned_data.get('time', datetime.time(12, 0))
            lesson_schedule.day_of_week = form.cleaned_data.get('day_of_week')
            lesson_schedule.save()
            return HttpResponseRedirect(reverse('day_detail', args=[year, month, day]))
        else:
            messages.error(request, "Formada səhvlər var. Zəhmət olmasa yoxlayın.")
    else:
        form = LessonScheduleForm(instance=lesson_schedule)

    return render(request, 'lessonSchedule/update_lesson_schedule.html', {
        'form': form,
        'lesson_schedule': lesson_schedule,
        'groups': Group.objects.all(),
        'next_url': request.GET.get('next', ''),
        'schedule_id' : request.GET.get('schedule_id', ''),
        'selected_year': request.GET.get('year', ''),
        'selected_month': request.GET.get('month', ''),
        'selected_day': request.GET.get('day', ''),
    })

def update_weekly_lesson_detail(request, schedule_id, year, month, day, week_offset):
    lesson_schedule = get_object_or_404(LessonSchedule, id=schedule_id)
    if request.method == 'POST':
        form = LessonScheduleForm(request.POST, instance=lesson_schedule)
        group_id = request.POST.get('group')
        group = get_object_or_404(Group, id=group_id)
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        try:
            start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, "Start date format is incorrect.")
            return redirect('update_weekly_lesson_detail', schedule_id=schedule_id, year=year, month=month, day=day, week_offset=week_offset)

        end_date = datetime.datetime.strptime(end_date_str, '%d/%m/%Y').date() if end_date_str else start_date

        if form.is_valid():
            lesson_schedule.group = group
            lesson_schedule.start_date = start_date
            lesson_schedule.end_date = end_date
            lesson_schedule.time = form.cleaned_data.get('time', datetime.time(12, 0))
            lesson_schedule.day_of_week = form.cleaned_data.get('day_of_week')
            lesson_schedule.save()
            return HttpResponseRedirect(reverse('week_day_detail', args=[year, month, day, week_offset]))
        else:
            messages.error(request, "There are errors in the form. Please check.")
    else:
        form = LessonScheduleForm(instance=lesson_schedule)

    return render(request, 'lessonSchedule/update_lesson_schedule.html', {
        'form': form,
        'lesson_schedule': lesson_schedule,
        'groups': Group.objects.all(),
        'next_url': request.GET.get('next', ''),
        'schedule_id': schedule_id,
        'year': year,
        'month': month,
        'day': day,
        'week_offset': week_offset,
    })

# Delete
def delete_lesson_schedule(request, schedule_id):
    lesson_schedule = get_object_or_404(LessonSchedule, id=schedule_id)
    lesson_schedule.delete()
    return redirect('daily_list')

def delete_lesson_detail(request, schedule_id, year, month, day):
    schedule = get_object_or_404(LessonSchedule, id=schedule_id)
    schedule.delete()
    return HttpResponseRedirect(reverse('day_detail', args=[year, month, day]))

def delete_group(request, pk):
    group = Group.objects.get(pk=pk)
    group.delete()
    return redirect('group_list')

def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    group_id = student.group.id  # Get the id of the group the student belongs to
    student.delete()
    return redirect('group_detail', group_id=group_id)  # Redirect to group detail page

def delete_student_pay(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('pay_day')  # Redirect to pay_day

# List
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group/group_list.html', {'groups': groups})

def daily_list(request):
    today = timezone.now().date()  # Get today's date

    # Retrieve schedules for today
    schedules = LessonSchedule.objects.filter(start_date=today).order_by('time')

    # Haftanın günlerini İngilizce olarak tanımla
    days_of_week_dict = {
        'Monday': 'Bazar Ertəsi',
        'Tuesday': 'Çərşənbə Axşamı',
        'Wednesday': 'Çərşənbə',
        'Thursday': 'Cümə Axşamı',
        'Friday': 'Cümə',
        'Saturday': 'Şənbə',
        'Sunday': 'Bazar',
    }

    if request.method == 'POST':
        group_id = request.POST.get('group')
        time_str = request.POST.get('time')

        if group_id and time_str:
            group = Group.objects.get(id=group_id)
            
            # Convert time_str to datetime.time object
            try:
                time = datetime.datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                print("Invalid time format:", time_str)
                # Handle the error as appropriate, e.g., add an error message to the form

            # Haftanın gününü İngilizce olarak al ve Azerbaijani seçeneğine dönüştür
            day_of_week_english = today.strftime('%A')
            day_of_week_azerbaijani = days_of_week_dict.get(day_of_week_english)

            new_lesson = LessonSchedule(
                group=group,
                start_date=today,
                end_date=today,
                time=time,
                day_of_week=day_of_week_azerbaijani  # Haftanın gününü ayarla
            )
            new_lesson.save()
            return HttpResponseRedirect(reverse('daily_list'))
    else:
        # Initialize the form with empty data
        form = LessonScheduleForm()

    translated_date = translate_month_name(today)

    context = {
        'today': translated_date,
        'schedules': schedules,
        'groups': Group.objects.all(),
        'form': LessonScheduleForm(),
        'date': today,  # Pass today's date to the template
    }
    return render(request, 'day/daily_list.html', context)

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group)
    total_payments = sum(student.price for student in students)
    
    next_url = request.GET.get('next', '')
    schedule_id = request.GET.get('schedule_id', '')
    selected_year = request.GET.get('year', '')
    selected_month = request.GET.get('month', '')
    selected_day = request.GET.get('day', '')
    week_offset = request.GET.get('week_offset', '')
    
    context = {
        'group': group,
        'students': students,
        'total_payments': total_payments,
        'next_url': next_url,
        'schedule_id': schedule_id,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_day': selected_day,
        'week_offset': week_offset,
    }
    
    return render(request, 'group/group_detail.html', context)

def translate_month_name(date):
    month_names = {
        1: "Yanvar",
        2: "Fevral",
        3: "Mart",
        4: "Aprel",
        5: "May",
        6: "İyun",
        7: "İyul",
        8: "Avqust",
        9: "Sentyabr",
        10: "Oktyabr",
        11: "Noyabr",
        12: "Dekabr",
    }
    month = month_names[date.month]
    day = date.day
    return f"{day} {month}"

def day_detail(request, year, month, day):
    date = datetime.date(year, month, day)
    schedules = LessonSchedule.objects.filter(start_date=date, end_date=date).order_by('time')

    # Haftanın günlerini İngilizce olarak tanımla
    days_of_week_dict = {
        'Monday': 'Bazar Ertəsi',
        'Tuesday': 'Çərşənbə Axşamı',
        'Wednesday': 'Çərşənbə',
        'Thursday': 'Cümə Axşamı',
        'Friday': 'Cümə',
        'Saturday': 'Şənbə',
        'Sunday': 'Bazar',
    }
    if request.method == 'POST':
        group_id = request.POST.get('group')
        time_str = request.POST.get('time')

        if group_id and time_str:
            group = Group.objects.get(id=group_id)
            # Convert time_str to datetime.time object
            try:
                time = datetime.datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                print("Invalid time format:", time_str)
                # Handle the error as appropriate, e.g., add an error message to the form

            # Haftanın gününü İngilizce olarak al ve Azerbaijani seçeneğine dönüştür
            day_of_week_english = date.strftime('%A')
            day_of_week_azerbaijani = days_of_week_dict.get(day_of_week_english)

            new_lesson = LessonSchedule(
                group=group,
                start_date=date,
                end_date=date,
                time=time,
                day_of_week=day_of_week_azerbaijani  # Haftanın gününü ayarla
            )
            new_lesson.save()
            return HttpResponseRedirect(reverse('day_detail', args=[year, month, day]))
    else:
        # Initialize the form with empty data
        form = LessonScheduleForm()

    translated_date = translate_month_name(date)
    groups = Group.objects.all()

    context = {
        'date': translated_date,
        'schedules': schedules,
        'groups': groups,
        'form': LessonScheduleForm(),  # Pass an empty form to the template
        'selected_day': day,
        'selected_month': month,
        'selected_year': year,
    }
    return render(request, 'day/day_detail.html', context)

def week_day_detail(request, year, month, day, week_offset):
    try:
        # String olarak gelen year, month, day ve week_offset parametrelerini integer'a çeviriyoruz
        year = int(year)
        month = int(month)
        day = int(day)
        week_offset = int(week_offset)
    except ValueError:
        return HttpResponseBadRequest("Invalid week_offset value")

    # Belirtilen günün tarihini al
    date = datetime.date(year, month, day)

    # Bu günün ders programlarını al
    schedules = LessonSchedule.objects.filter(start_date=date, end_date=date).order_by('time')

    # Aynı haftaya geri dönüş için haftanın başlangıç ve bitiş tarihlerini hesapla
    start_of_week = date - datetime.timedelta(days=date.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    start_of_week_str = f"{start_of_week.day} {get_month_name(start_of_week.month)}"
    end_of_week_str = f"{end_of_week.day} {get_month_name(end_of_week.month)}"

    # Haftanın günlerini İngilizce olarak tanımla
    days_of_week_dict = {
        'Monday': 'Bazar Ertəsi',
        'Tuesday': 'Çərşənbə Axşamı',
        'Wednesday': 'Çərşənbə',
        'Thursday': 'Cümə Axşamı',
        'Friday': 'Cümə',
        'Saturday': 'Şənbə',
        'Sunday': 'Bazar',
    }
    if request.method == 'POST':
        group_id = request.POST.get('group')
        time_str = request.POST.get('time')
        if group_id and time_str:
            group = Group.objects.get(id=group_id)
            # Convert time_str to datetime.time object
            try:
                time = datetime.datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                print("Invalid time format:", time_str)
                # Handle the error as appropriate, e.g., add an error message to the form

            # Haftanın gününü İngilizce olarak al ve Azerbaijani seçeneğine dönüştür
            day_of_week_english = date.strftime('%A')
            day_of_week_azerbaijani = days_of_week_dict.get(day_of_week_english)
                
            new_lesson = LessonSchedule(
                group=group,
                start_date=date,
                end_date=date,
                time=time,
                day_of_week=day_of_week_azerbaijani  # Haftanın gününü ayarla
            )
            new_lesson.save()
            return HttpResponseRedirect(reverse('week_day_detail', args=[year, month, day, week_offset]))
    else:
        # Initialize the form with empty data
        form = LessonScheduleForm()

    translated_date = translate_month_name(date)
    groups = Group.objects.all()

    context = {
        'schedules': schedules,
        'date': translated_date,
        'groups': groups,
        'form': LessonScheduleForm(),  # Pass an empty form to the template
        'start_of_week': start_of_week_str,
        'end_of_week': end_of_week_str,
        'week_offset': week_offset,
        'day': day,
        'month': month,
        'year': year,
    }
    return render(request, 'weekly/week_day_detail.html', context)

def get_month_name(month_number):
    months = [
        'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun',
        'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr'
    ]
    return months[month_number - 1]

def weekly_schedule_view(request, week_offset=0):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=int(week_offset))
    end_of_week = start_of_week + timedelta(days=6)

    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]

    schedules = LessonSchedule.objects.filter(start_date__lte=end_of_week, end_date__gte=start_of_week).order_by('time')

    # Format dates for Azerbaycan language
    start_of_week_str = f"{start_of_week.day} {get_month_name(start_of_week.month)}"
    end_of_week_str = f"{end_of_week.day} {get_month_name(end_of_week.month)}"

    context = {
        'schedules': schedules,
        'start_of_week': start_of_week_str,
        'end_of_week': end_of_week_str,
        'week_offset': int(week_offset),
        'days_of_week': days_of_week,
        'today': today
    }
    return render(request, 'weekly/weekly_schedule.html', context)

def pay_day(request):
    now = datetime.datetime.now()
    today = now.date()
    end_date_range = today - timedelta(days=27)
    
    expired_students = Student.objects.filter(
        Q(end_date=today) | Q(end_date__range=(end_date_range, today))
    )
    return render(request, 'student/pay_day.html', {'expired_students': expired_students})

def renew_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Update the student's records
    student.add_date = student.end_date
    student.end_date = student.add_date + relativedelta(months=1)
    student.save()
    return redirect('pay_day')

def calendar_view(request):
    today = timezone.now().date()
    year = request.GET.get('year', today.year)
    month = request.GET.get('month', today.month)
    
    year = int(year)
    month = int(month)
    
    # Get the first and last day of the month
    first_day_of_month = datetime.date(year, month, 1)
    _, last_day = monthrange(year, month)
    last_day_of_month = datetime.date(year, month, last_day)
    
    # Get all groups for the selected month
    groups = LessonSchedule.objects.filter(start_date__range=(first_day_of_month, last_day_of_month)).order_by('time')

    # Prepare the days in the month, grouped by week
    cal = Calendar()
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        week_days = []
        for day in week:
            if day.month == month:
                day_groups = groups.filter(start_date=day)
                week_days.append((day, day_groups, day.weekday() == 6))  # Sunday is represented by 6
            else:
                week_days.append((day, [], False))
        weeks.append(week_days)
    
    # Prepare the months for the dropdown
    months = list(range(1, 13))
    
    context = {
        'weeks': weeks,
        'current_month': today.month,
        'current_year': today.year,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'today': today,
    }
    return render(request, 'calendar/calendar.html', context)

# User
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('group_list')
        else:
            messages.error(request, 'İstifadəçi adı və ya parol səhvdir.')
    return render(request, 'account/login.html')

def user_logout(request):
    logout(request)
    return redirect('group_list')

def generate_pdf_daily(request):
    today = timezone.now().date()  # Get today's date
    translated_date = translate_month_name(today)

    # Retrieve dynamic data
    schedules = LessonSchedule.objects.filter(start_date=today).order_by('time')

    # Render the template to a string
    html_content = render_to_string('day/daily_list_pdf.html', {
        'today': translated_date,
        'schedules': schedules,
    })

    # Specify the path to wkhtmltopdf
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Generate the PDF as a binary string
    pdf_content = pdfkit.from_string(html_content, False, configuration=config)

    # Create an HttpResponse object with the appropriate headers for file download
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="gunluk_dersler.pdf"'

    return response

def generate_pdf_weekly(request):
    week_offset = int(request.GET.get('week_offset', 0))
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=int(week_offset))
    end_of_week = start_of_week + timedelta(days=6)

    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]

    schedules = LessonSchedule.objects.filter(start_date__lte=end_of_week, end_date__gte=start_of_week).order_by('time')

    # Format dates for Azerbaycan language
    start_of_week_str = f"{start_of_week.day} {get_month_name(start_of_week.month)}"
    end_of_week_str = f"{end_of_week.day} {get_month_name(end_of_week.month)}"

    # Render the template to a string
    html_content = render_to_string('weekly/weekly_schedule_pdf.html', {
        'schedules': schedules,
        'start_of_week': start_of_week_str,
        'end_of_week': end_of_week_str,
        'days_of_week': days_of_week,
    })

    # Specify the path to wkhtmltopdf
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Set PDF options for landscape orientation and fit-to-page settings
    options = {
        'orientation': 'Landscape',
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'dpi': 300,
        'zoom': 1,  # Scale down content to fit everything on one page
    }

    # Generate the PDF as a binary string
    pdf_content = pdfkit.from_string(html_content, False, configuration=config, options=options)

    # Create an HttpResponse object with the appropriate headers for file download
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="heftelik_dersler_{start_of_week_str}_-_{end_of_week_str}.pdf"'

    return response

def generate_pdf_calendar(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Get the first and last day of the month
    first_day_of_month = datetime.date(year, month, 1)
    _, last_day = monthrange(year, month)
    last_day_of_month = datetime.date(year, month, last_day)
    
    # Get all groups for the selected month
    groups = LessonSchedule.objects.filter(start_date__range=(first_day_of_month, last_day_of_month)).order_by('time')

    # Prepare the days in the month, grouped by week
    cal = Calendar()
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        week_days = []
        for day in week:
            if day.month == month:
                day_groups = groups.filter(start_date=day)
                week_days.append((day, day_groups, day.weekday() == 6))  # Sunday is represented by 6
            else:
                week_days.append((day, [], False))
        weeks.append(week_days)
    
    # Prepare the months for the dropdown
    months = list(range(1, 13))

    # Render the template to a string
    html_content = render_to_string('calendar/calendar_pdf.html', {
        'weeks': weeks,
        'current_month': today.month,
        'current_year': today.year,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'today': today,
    })

    # Specify the path to wkhtmltopdf
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Set PDF options for landscape orientation and fit-to-page settings
    options = {
        'orientation': 'Landscape',
        'page-size': 'A4',
        'margin-top': '0mm',
        'margin-right': '0mm',
        'margin-bottom': '0mm',
        'margin-left': '0mm',
        'dpi': 300,
        'zoom': 0.83,  # Scale down content to fit everything on one page
    }

    # Generate the PDF as a binary string
    pdf_content = pdfkit.from_string(html_content, False, configuration=config, options=options)

    # Create an HttpResponse object with the appropriate headers for file download
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="calendar_{year}_{month}.pdf"'

    return response