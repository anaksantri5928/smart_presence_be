from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    """Custom User model for students and lecturers"""
    ROLE_CHOICES = [
        ('mahasiswa', 'Mahasiswa'),
        ('dosen', 'Dosen'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    nim = models.CharField(max_length=20, blank=True, null=True)  # Student ID
    nidn = models.CharField(max_length=20, blank=True, null=True)  # Lecturer ID
    token = models.CharField(max_length=100, blank=True, null=True)  # Authentication token
    token_created = models.DateTimeField(blank=True, null=True)  # Token creation time
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Attendance(models.Model):
    """Attendance model to track student attendance"""
    STATUS_CHOICES = [
        ('Hadir', 'Hadir'),
        ('Tidak Hadir', 'Tidak Hadir'),
        ('Izin', 'Izin'),
        ('Sakit', 'Sakit'),
    ]
    
    nim = models.CharField(max_length=20)
    nama = models.CharField(max_length=100)
    mata_kuliah = models.CharField(max_length=100)
    tanggal = models.DateField()
    waktu = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Hadir')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-tanggal', '-waktu']
        unique_together = ['nim', 'mata_kuliah', 'tanggal']
    
    def __str__(self):
        return f"{self.nim} - {self.mata_kuliah} - {self.tanggal}"
