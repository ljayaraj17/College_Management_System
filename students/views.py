from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from .models import StudentProfile
from .forms import StudentProfileForm
from placements.models import JobPosting, Application

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student

class StudentProfileView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = StudentProfile
    template_name = 'students/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.student_profile

class StudentProfileUpdateView(LoginRequiredMixin, StudentRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'students/profile_form.html'
    success_url = reverse_lazy('student_profile')

    def get_object(self):
        return self.request.user.student_profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class InternshipListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = JobPosting
    template_name = 'students/internship_list.html'
    context_object_name = 'jobs'
    ordering = ['-created_at']

    def get_queryset(self):
        return JobPosting.objects.filter(is_active=True, deadline__gte=timezone.now()).order_by('-created_at')

class InternshipDetailView(LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = JobPosting
    template_name = 'students/internship_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if student has already applied
        context['has_applied'] = Application.objects.filter(
            student=self.request.user, 
            job=self.object
        ).exists()
        return context

class ApplicationListView(LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Application
    template_name = 'students/application_list.html'
    context_object_name = 'applications'
    ordering = ['-applied_at']

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user).select_related('job').order_by('-applied_at')

def apply_job(request, job_id):
    if not request.user.is_authenticated or not request.user.is_student:
        return redirect('login')
    
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, id=job_id)
        
        # Check if already applied
        if Application.objects.filter(student=request.user, job=job).exists():
            messages.warning(request, "You have already applied for this position.")
        else:
            Application.objects.create(student=request.user, job=job)
            messages.success(request, f"Successfully applied to {job.title} at {job.company}!")
        
        return redirect('internship_detail', pk=job.id)
    
    return redirect('internship_list')
