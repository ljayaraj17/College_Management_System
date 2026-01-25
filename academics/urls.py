from django.urls import path
from .views import (
    DepartmentListView, DepartmentCreateView,
    CourseListView, CourseCreateView,
    SubjectListView, SubjectCreateView,
    EnrollmentListView, EnrollmentCreateView,
    TimetableListView, TimetableCreateView,
    TimeSlotListView, TimeSlotCreateView,
)

urlpatterns = [
    # Departments
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', DepartmentCreateView.as_view(), name='department_create'),
    
    # Courses
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/add/', CourseCreateView.as_view(), name='course_create'),
    
    # Subjects
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', SubjectCreateView.as_view(), name='subject_create'),
    
    # Enrollments
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/add/', EnrollmentCreateView.as_view(), name='enrollment_create'),
    
    # Timetable
    path('timetable/', TimetableListView.as_view(), name='timetable_list'),
    path('timetable/add/', TimetableCreateView.as_view(), name='timetable_create'),
    
    # Time Slots
    path('timeslots/', TimeSlotListView.as_view(), name='timeslot_list'),
    path('timeslots/add/', TimeSlotCreateView.as_view(), name='timeslot_create'),
]

