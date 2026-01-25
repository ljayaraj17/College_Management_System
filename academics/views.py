from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Department, Course, Subject, Enrollment, TimeSlot, Timetable
from users.mixins import AdminRequiredMixin, HODRequiredMixin, FacultyRequiredMixin, StudentRequiredMixin


# Department Views
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'academics/department_list.html'
    context_object_name = 'departments'
    
    def dispatch(self, request, *args, **kwargs):
        # Allow Super Admin and Admin access
        if not (request.user.is_super_admin or request.user.is_admin):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    fields = ['name', 'code', 'hod', 'description', 'is_active']
    template_name = 'academics/department_form.html'
    success_url = reverse_lazy('department_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Allow Super Admin and Admin access
        if not (request.user.is_super_admin or request.user.is_admin):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "Department created successfully!")
        return super().form_valid(form)


# Course Views
class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'academics/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        # HOD can only see courses in their department
        if self.request.user.is_hod and self.request.user.department_fk:
            queryset = queryset.filter(department=self.request.user.department_fk)
        return queryset


class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Course
    fields = ['name', 'code', 'department', 'duration_years', 'description', 'is_active']
    template_name = 'academics/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)


# Subject Views
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'academics/subject_list.html'
    context_object_name = 'subjects'
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True).select_related('course', 'department', 'faculty')
        # Filter by department if HOD
        if self.request.user.is_hod and self.request.user.department_fk:
            queryset = queryset.filter(department=self.request.user.department_fk)
        # Filter by faculty if Faculty
        elif self.request.user.is_faculty:
            queryset = queryset.filter(faculty=self.request.user)
        return queryset


class SubjectCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Subject
    fields = ['name', 'code', 'course', 'credits', 'semester', 'department', 'faculty', 'description', 'is_active']
    template_name = 'academics/subject_form.html'
    success_url = reverse_lazy('subject_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Subject created successfully!")
        return super().form_valid(form)


# Enrollment Views
class EnrollmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Enrollment
    template_name = 'academics/enrollment_list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        queryset = Enrollment.objects.filter(is_active=True).select_related('student', 'course')
        # HOD can only see enrollments in their department
        if self.request.user.is_hod and self.request.user.department_fk:
            queryset = queryset.filter(course__department=self.request.user.department_fk)
        return queryset


class EnrollmentCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Enrollment
    fields = ['student', 'course', 'enrollment_date', 'current_semester', 'academic_year', 'batch', 'is_active']
    template_name = 'academics/enrollment_form.html'
    success_url = reverse_lazy('enrollment_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Student enrolled successfully!")
        return super().form_valid(form)


# Timetable Views
class TimetableListView(LoginRequiredMixin, ListView):
    model = Timetable
    template_name = 'academics/timetable_list.html'
    context_object_name = 'timetables'
    
    def get_queryset(self):
        queryset = Timetable.objects.filter(is_active=True).select_related(
            'subject', 'time_slot', 'faculty'
        )
        
        # Students see their batch timetable
        if self.request.user.is_student:
            # Get student's enrollment to find batch
            enrollment = Enrollment.objects.filter(
                student=self.request.user,
                is_active=True
            ).first()
            if enrollment:
                queryset = queryset.filter(
                    batch=enrollment.batch,
                    academic_year=enrollment.academic_year
                )
        
        # Faculty see their subjects
        elif self.request.user.is_faculty:
            queryset = queryset.filter(faculty=self.request.user)
        
        # HOD see their department
        elif self.request.user.is_hod and self.request.user.department_fk:
            queryset = queryset.filter(subject__department=self.request.user.department_fk)
        
        return queryset.order_by('time_slot__day_of_week', 'time_slot__start_time')


class TimetableCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Timetable
    fields = ['subject', 'time_slot', 'room', 'faculty', 'batch', 'semester', 'academic_year', 'is_active']
    template_name = 'academics/timetable_form.html'
    success_url = reverse_lazy('timetable_list')
    
    def form_valid(self, form):
        # Check for conflicts
        timetable = form.save(commit=False)
        conflicts = timetable.check_conflicts()
        
        if conflicts['has_conflicts']:
            messages.warning(
                self.request,
                "Warning: Timetable conflicts detected! Please review before saving."
            )
        
        messages.success(self.request, "Timetable entry created successfully!")
        return super().form_valid(form)


# TimeSlot Views
class TimeSlotListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'academics/timeslot_list.html'
    context_object_name = 'timeslots'


class TimeSlotCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = TimeSlot
    fields = ['day_of_week', 'start_time', 'end_time']
    template_name = 'academics/timeslot_form.html'
    success_url = reverse_lazy('timeslot_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Time slot created successfully!")
        return super().form_valid(form)
