from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from academics.models import Subject

class Attendance(models.Model):
    """Daily attendance records"""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'STUDENT'}
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABSENT')
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendances',
        limit_choices_to={'role': 'FACULTY'}
    )
    remarks = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        unique_together = [['student', 'subject', 'date']]
        indexes = [
            models.Index(fields=['student', 'subject', 'date']),
            models.Index(fields=['subject', 'date']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - {self.date} ({self.status})"


class AttendanceSummary(models.Model):
    """Aggregated attendance summary per student per subject per semester"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        limit_choices_to={'role': 'STUDENT'}
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_summaries')
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(16)],
        help_text="Semester number"
    )
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    
    total_classes = models.IntegerField(default=0, help_text="Total classes conducted")
    present_count = models.IntegerField(default=0, help_text="Number of present days")
    absent_count = models.IntegerField(default=0, help_text="Number of absent days")
    late_count = models.IntegerField(default=0, help_text="Number of late days")
    excused_count = models.IntegerField(default=0, help_text="Number of excused days")
    
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Attendance percentage"
    )
    
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-academic_year', 'semester', 'student']
        verbose_name = "Attendance Summary"
        verbose_name_plural = "Attendance Summaries"
        unique_together = [['student', 'subject', 'semester', 'academic_year']]
        indexes = [
            models.Index(fields=['student', 'subject', 'semester']),
        ]

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} - Sem {self.semester} ({self.attendance_percentage}%)"
    
    def calculate_percentage(self):
        """Calculate attendance percentage"""
        if self.total_classes == 0:
            self.attendance_percentage = 0.0
        else:
            # Count present and late as attended
            attended = self.present_count + self.late_count
            self.attendance_percentage = (attended / self.total_classes) * 100
        self.save()
        return self.attendance_percentage
    
    def update_from_records(self):
        """Update summary from attendance records"""
        from django.db.models import Count, Q
        from django.utils import timezone
        
        # Get all attendance records for this student, subject, semester, academic_year
        # Note: We need to determine semester from date or enrollment
        records = Attendance.objects.filter(
            student=self.student,
            subject=self.subject
        )
        
        # Filter by academic year (simplified - you may need to adjust based on your date logic)
        self.present_count = records.filter(status='PRESENT').count()
        self.absent_count = records.filter(status='ABSENT').count()
        self.late_count = records.filter(status='LATE').count()
        self.excused_count = records.filter(status='EXCUSED').count()
        self.total_classes = records.count()
        
        self.calculate_percentage()
        return self.attendance_percentage
