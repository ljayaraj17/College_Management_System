from django import forms
from .models import StudentProfile
from users.models import User

class StudentProfileForm(forms.ModelForm):
    # Include department from User model
    department = forms.CharField(max_length=100, required=False, help_text="Department")
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'department', 'batch', 'profile_photo', 'bio', 'cgpa', 'linkedin_url', 'github_url', 'resume', 'cover_letter', 'skills', 'stem_badge', 'aiml_cert']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Python, Django, Machine Learning...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.FileInput(attrs={'class': 'form-control'}),
            'stem_badge': forms.FileInput(attrs={'class': 'form-control'}),
            'aiml_cert': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['department'].initial = user.department
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Save user fields
            if self.cleaned_data.get('department'):
                profile.user.department = self.cleaned_data['department']
            if self.cleaned_data.get('first_name'):
                profile.user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name'):
                profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
        return profile
