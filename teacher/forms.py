from django import forms
from .models import Group, Student, LessonSchedule
from datetime import datetime, date

class CustomDateInput(forms.DateInput):
    input_type = 'text'
    format = '%d/%m/%Y'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        if value:
            if isinstance(value, (datetime, date)):
                return value.strftime(self.format)
        return value

class StudentForm(forms.ModelForm):
    add_date = forms.CharField(widget=CustomDateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY'}))

    class Meta:
        model = Student
        fields = ['group', 'full_name', 'price', 'grade', 'add_date', 'student_mobile', 'parent_mobile']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # If creating a new form
            self.fields['add_date'].initial = date.today().strftime('%d/%m/%Y')

    def clean_add_date(self):
        add_date = self.cleaned_data['add_date']
        try:
            return datetime.strptime(add_date, '%d/%m/%Y').date()
        except ValueError:
            raise forms.ValidationError("Tarixi DD/MM/YYYY formatında daxil edin.")

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name',]

class LessonScheduleForm(forms.ModelForm):
    class Meta:
        model = LessonSchedule
        fields = ['day_of_week', 'time']
        labels = {
            'day_of_week': 'Həftənin Günü',
            'time': 'Saat',
        }
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(format='%H:%M'),
        }