from django.urls import path
from .views import (
    StudentProfileView, 
    StudentProfileUpdateView,
    InternshipListView,
    InternshipDetailView,
    ApplicationListView,
    apply_job
)
from .certificate_views import (
    CertificateCreateView,
    CertificateListView,
    CertificateDeleteView
)

urlpatterns = [
    path('profile/', StudentProfileView.as_view(), name='student_profile'),
    path('profile/edit/', StudentProfileUpdateView.as_view(), name='student_profile_edit'),
    
    path('internships/', InternshipListView.as_view(), name='internship_list'),
    path('internships/<int:pk>/', InternshipDetailView.as_view(), name='internship_detail'),
    
    path('applications/', ApplicationListView.as_view(), name='application_list'),
    path('apply/<int:job_id>/', apply_job, name='apply_job'),
    
    # Certificate/Badge management
    path('certificates/', CertificateListView.as_view(), name='certificate_list'),
    path('certificates/add/', CertificateCreateView.as_view(), name='add_badge'),
    path('certificates/<int:pk>/delete/', CertificateDeleteView.as_view(), name='certificate_delete'),
]
