from django.contrib import admin
from .models import Attendance, AttendanceSummary

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'marked_by', 'created_at']
    list_filter = ['status', 'date', 'subject', 'created_at']
    search_fields = ['student__username', 'student__email', 'subject__name']
    raw_id_fields = ['student', 'subject', 'marked_by']
    date_hierarchy = 'date'

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'academic_year', 'attendance_percentage', 'total_classes']
    list_filter = ['semester', 'academic_year', 'subject']
    search_fields = ['student__username', 'subject__name']
    raw_id_fields = ['student', 'subject']
    readonly_fields = ['last_calculated']
