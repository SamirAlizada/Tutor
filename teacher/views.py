from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.forms import formset_factory
from calendar import Calendar, monthrange
from .models import Group, Student, LessonSchedule
from .forms import GroupForm, StudentForm, LessonScheduleForm
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from .forms import LessonScheduleForm
import datetime
from django.http import HttpResponseRedirect

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
        group = Group.objects.get(id=group_id)
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        try:
            # Parse start_date
            start_date = datetime.datetime.strptime(start_date_str, '%d/%m/%Y').date()
        except ValueError:
            messages.error(request, "Start date format is incorrect.")
            return redirect('add_lesson_schedule')

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
            messages.error(request, "Formada səhvlər var. Zəhmət olmasa yoxlayın.")
    else:
        formset = LessonScheduleFormSet()

    return render(request, 'lessonSchedule/add_lesson_schedule.html', {'formset': formset, 'groups': groups})

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
def update_lesson_schedule(request, schedule_id):
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
            return redirect('daily_list')
        else:
            messages.error(request, "Formada səhvlər var. Zəhmət olmasa yoxlayın.")
    else:
        form = LessonScheduleForm(instance=lesson_schedule)

    return render(request, 'lessonSchedule/update_lesson_schedule.html', {
        'form': form,
        'lesson_schedule': lesson_schedule,
        'groups': Group.objects.all()
    })

def update_student(request, pk, group_id):
    student = get_object_or_404(Student, pk=pk)
    group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'student/update_student.html', {'form': form, 'group': group})

def update_student_pay(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(instance=student)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('pay_day')
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
        'groups': Group.objects.all()
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
        print("Form errors:", form.errors)

    translated_date = translate_month_name(today)

    context = {
        'today': translated_date,
        'schedules': schedules,
        'groups': Group.objects.all(),
        'form': LessonScheduleForm(),
        'date': today,  # Pass today's date to the template
    }
    return render(request, 'daily_list.html', context)

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group)
    total_payments = sum(student.price for student in students)
    
    next_url = request.GET.get('next', '')
    schedule_id = request.GET.get('schedule_id', '')
    selected_year = request.GET.get('year', '')
    selected_month = request.GET.get('month', '')
    selected_day = request.GET.get('day', '')
    
    context = {
        'group': group,
        'students': students,
        'total_payments': total_payments,
        'next_url': next_url,
        'schedule_id': schedule_id,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_day': selected_day,
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

    if request.method == 'POST':
        group_id = request.POST.get('group')
        time = request.POST.get('time')

        if group_id and time:
            group = Group.objects.get(id=group_id)
            new_lesson = LessonSchedule(
                group=group,
                start_date=date,
                end_date=date,
                time=time,
                day_of_week=date.strftime('%A')  # Get the day of the week
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
    return render(request, 'day_detail.html', context)

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
                week_days.append((day, day_groups))
            else:
                week_days.append((day, []))
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
    return render(request, 'calendar.html', context)

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