from django import forms
from .models import BorrowRecord, Book, Fine
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AdminIssueBookForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role='STUDENT', is_approved=True),
        label="Student",
        widget=forms.Select(attrs={'class': 'form-select search-select'})
    )
    book = forms.ModelChoiceField(
        queryset=Book.objects.filter(available_copies__gt=0),
        label="Book",
        widget=forms.Select(attrs={'class': 'form-select search-select'})
    )
    issue_date = forms.DateTimeField(
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    due_date = forms.DateTimeField(
        initial=lambda: timezone.now() + timezone.timedelta(days=14),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

    class Meta:
        model = BorrowRecord
        fields = ['student', 'book', 'issue_date', 'due_date', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure only available books are listed when creating a new record
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

class AdminUpdateFineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = ['amount', 'paid']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
