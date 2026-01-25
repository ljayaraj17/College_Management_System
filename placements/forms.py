from django import forms
from .models import JobPosting

class JobPostingForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text="Format: YYYY-MM-DD HH:MM"
    )

    class Meta:
        model = JobPosting
        fields = ['title', 'company', 'department', 'description', 'competencies', 'stipend_range', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'competencies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, Java, Communication...'}),
            'stipend_range': forms.TextInput(attrs={'class': 'form-control'}),
        }
