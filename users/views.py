from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import CustomUserCreationForm, FacultyCreationForm, AdminCreationForm
from .models import User
from .mixins import AdminRequiredMixin, SuperAdminRequiredMixin, HODRequiredMixin
from .utils import send_approval_email

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Set session to expire when browser closes
            self.request.session.set_expiry(0)
        else:
            # Set session to expire in 2 weeks
            self.request.session.set_expiry(1209600)  # 14 days in seconds
        return super().form_valid(form)

class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('login')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['role'] = user.get_role_display()
        context['user'] = user
        
        # Role-specific context
        if user.is_student:
            context.update(self.get_student_context())
        elif user.is_faculty:
            context.update(self.get_faculty_context())
        elif user.is_super_admin or user.is_admin:
            context.update(self.get_admin_context())
        elif user.is_hod:
            context.update(self.get_hod_context())
        elif user.is_placement_cell or user.is_placement_officer:
            context.update(self.get_placement_context())
        
        return context
    
    def get_student_context(self):
        """Context for student dashboard"""
        from placements.models import Application, JobPosting
        from interviews.models import InterviewSchedule
        from django.utils import timezone
        
        return {
            'pending_applications': Application.objects.filter(
                student=self.request.user, 
                status='APPLIED'
            ).count(),
            'upcoming_interviews': InterviewSchedule.objects.filter(
                application__student=self.request.user,
                status='SCHEDULED',
                date_time__gte=timezone.now()
            ).count(),
            'active_jobs': JobPosting.objects.filter(
                is_active=True,
                deadline__gte=timezone.now()
            ).count(),
            'profile_completeness': getattr(
                self.request.user, 'student_profile', None
            ).get_profile_completeness() if hasattr(self.request.user, 'student_profile') else 0,
        }
    
    def get_faculty_context(self):
        """Context for faculty dashboard"""
        from placements.models import Application
        from django.db.models import Count
        
        return {
            'pending_approvals': Application.objects.filter(
                faculty_approved=False,
                status='APPLIED'
            ).count(),
            'total_students': self.request.user.department_fk.members.filter(
                role='STUDENT'
            ).count() if self.request.user.department_fk else 0,
        }
    
    def get_admin_context(self):
        """Context for admin/super admin dashboard"""
        from academics.models import Department
        from placements.models import JobPosting, Application
        
        return {
            'total_users': User.objects.count(),
            'pending_approvals': User.objects.filter(
                is_approved=False, is_active=False
            ).count(),
            'total_departments': Department.objects.filter(is_active=True).count() if Department.objects.exists() else 0,
            'active_jobs': JobPosting.objects.filter(is_active=True).count() if JobPosting.objects.exists() else 0,
            'total_applications': Application.objects.count() if Application.objects.exists() else 0,
        }
    
    def get_hod_context(self):
        """Context for HOD dashboard"""
        from academics.models import Department
        
        dept = self.request.user.department_fk
        if not dept:
            return {}
        
        return {
            'department': dept,
            'faculty_count': dept.members.filter(role='FACULTY').count(),
            'student_count': dept.members.filter(role='STUDENT').count(),
            'pending_faculty_approvals': User.objects.filter(
                role='FACULTY',
                department_fk=dept,
                is_approved=False
            ).count(),
        }
    
    def get_placement_context(self):
        """Context for placement officer dashboard"""
        from placements.models import JobPosting, Application
        from django.utils import timezone
        
        return {
            'active_jobs': JobPosting.objects.filter(is_active=True).count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(
                status='APPLIED'
            ).count(),
            'upcoming_interviews': Application.objects.filter(
                status='INTERVIEW'
            ).count(),
        }
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is approved
        if request.user.is_authenticated and not request.user.is_approved and request.user.role != 'STUDENT':
            from django.contrib import messages
            messages.warning(request, "Your account is pending approval. Please wait for admin approval.")
        return super().dispatch(request, *args, **kwargs)

class UserApprovalListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List view for pending user approvals"""
    model = User
    template_name = 'users/user_approval.html'
    context_object_name = 'pending_users'
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(is_approved=False, is_active=False).order_by('-date_joined')
        
        # Filter based on role permissions
        if user.role == 'SUPER_ADMIN':
            # Super Admin can see all pending users
            return queryset
        elif user.role == 'ADMIN':
            # Admin can see Students, Placement Officers, Faculty
            return queryset.filter(role__in=['STUDENT', 'PLACEMENT_OFFICER', 'FACULTY'])
        elif user.role == 'HOD':
            # HOD can only see Faculty in their department
            if user.department_fk:
                return queryset.filter(role='FACULTY', department_fk=user.department_fk)
            return User.objects.none()
        
        return User.objects.none()

@require_POST
def approve_user(request, pk):
    """Approve or reject a user account"""
    if not request.user.can_approve_users():
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')
    
    user_to_approve = get_object_or_404(User, pk=pk)
    action = request.POST.get('action')
    
    # Check if current user has permission to approve this user
    if request.user.role == 'HOD':
        # HOD can only approve Faculty in their department
        if user_to_approve.role != 'FACULTY' or user_to_approve.department_fk != request.user.department_fk:
            messages.error(request, "You can only approve Faculty members in your department.")
            return redirect('user_approval')
    elif request.user.role == 'ADMIN':
        # Admin can approve Students, Placement Officers, Faculty (but not Admin/HOD)
        if user_to_approve.role in ['ADMIN', 'HOD', 'SUPER_ADMIN']:
            messages.error(request, "You cannot approve users with Admin or higher roles.")
            return redirect('user_approval')
    
    if action == 'approve':
        user_to_approve.is_approved = True
        user_to_approve.is_active = True
        user_to_approve.approved_by = request.user
        user_to_approve.approved_at = timezone.now()
        user_to_approve.save()
        
        # Send email notification
        send_approval_email(user_to_approve, approved=True)
        
        messages.success(request, f"Approved user account: {user_to_approve.username}")
    elif action == 'reject':
        # Send rejection email before deletion
        send_approval_email(user_to_approve, approved=False)
        user_to_approve.delete()
        messages.success(request, f"Rejected (deleted) user account: {user_to_approve.username}")
        
    return redirect('user_approval')

# Keep old view for backward compatibility
class StudentApprovalListView(UserApprovalListView):
    """Legacy view - redirects to new user approval"""
    def get_queryset(self):
        return User.objects.filter(role='STUDENT', is_active=False, is_approved=False).order_by('-date_joined')

@require_POST
def approve_student(request, pk):
    """Legacy function - redirects to new approve_user"""
    return approve_user(request, pk)

class FacultyListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'users/faculty_list.html'
    context_object_name = 'faculty_members'
    
    def get_queryset(self):
        queryset = User.objects.filter(role='FACULTY')
        # HOD can only see faculty in their department
        if self.request.user.role == 'HOD' and self.request.user.department_fk:
            queryset = queryset.filter(department_fk=self.request.user.department_fk)
        return queryset

class FacultyCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = FacultyCreationForm
    template_name = 'users/faculty_form.html'
    success_url = reverse_lazy('faculty_list')

    def form_valid(self, form):
        form.instance.role = 'FACULTY'
        form.instance.is_approved = True  # Auto-approve if created by admin
        form.instance.is_active = True
        form.instance.approved_by = self.request.user
        form.instance.approved_at = timezone.now()
        messages.success(self.request, "Faculty member added successfully!")
        return super().form_valid(form)
