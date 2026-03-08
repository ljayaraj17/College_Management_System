from django.urls import path
from .views import (
    LibraryBookListView,
    RequestBookView,
    ReserveBookView,
    MyBooksView,
    AdminLibraryDashboardView,
    AdminIssueBookView,
    AdminApproveRequestView,
    AdminReturnBookView,
    AdminUpdateFineView,
)

app_name = 'library'

urlpatterns = [
    # Student URLs
    path('books/', LibraryBookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/request/', RequestBookView.as_view(), name='request_book'),
    path('books/<int:book_id>/reserve/', ReserveBookView.as_view(), name='reserve_book'),
    path('my-books/', MyBooksView.as_view(), name='my_books'),
    
    # Admin URLs
    path('admin/dashboard/', AdminLibraryDashboardView.as_view(), name='admin_dashboard'),
    path('admin/issue/', AdminIssueBookView.as_view(), name='admin_issue_book'),
    path('admin/approve/<int:record_id>/', AdminApproveRequestView.as_view(), name='admin_approve_request'),
    path('admin/return/<int:record_id>/', AdminReturnBookView.as_view(), name='admin_return_book'),
    path('admin/fine/<int:pk>/update/', AdminUpdateFineView.as_view(), name='admin_update_fine'),
]
