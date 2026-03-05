from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Announcement, AnnouncementCategory
from users.mixins import AdminRequiredMixin

class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    
    def get_queryset(self):
        # Users see announcements relevant to them or global ones
        user = self.request.user
        if user.is_super_admin or user.is_admin:
            return Announcement.objects.all().order_by('-posted_at')
        
        # Filtering for Student/Faculty/HOD
        queryset = Announcement.objects.filter(is_active=True).order_by('-is_pinned', '-posted_at')
        # Logic to filter by target_audience would go here or handled in template
        # For now, return all active ones
        return queryset

class AnnouncementCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Announcement
    fields = ['title', 'content', 'category', 'priority', 'target_audience', 'target_department', 'target_batch', 'expiry_date', 'attachment', 'is_pinned']
    template_name = 'announcements/announcement_form.html'
    success_url = reverse_lazy('announcement_list')
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, "Announcement published successfully!")
        return super().form_valid(form)

class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'
