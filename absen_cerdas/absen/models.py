from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('mahasiswa', 'Mahasiswa'),
        ('dosen', 'Dosen'),
    ]

    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'role']

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Class(models.Model):
    name = models.CharField(max_length=255)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'dosen'}, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FaceEmbedding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    embedding = models.JSONField()  # Store as list of floats
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embedding for {self.user.username}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.class_id.name} - {self.timestamp}"