from rest_framework import serializers
from .models import User, Attendance
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nama', 'role', 'nim', 'nidn']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        role = data.get('role')
        
        if not username or not role:
            raise serializers.ValidationError("Username and role are required")
        
        try:
            user = User.objects.get(username=username, role=role)
        except User.DoesNotExist:
            raise serializers.ValidationError("User tidak ditemukan")
        
        data['user'] = user
        return data

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['nim', 'nama', 'mata_kuliah', 'tanggal', 'waktu', 'status']
        read_only_fields = ['tanggal', 'waktu', 'status']

class AttendanceCreateSerializer(serializers.Serializer):
    nim = serializers.CharField(max_length=20)
    mata_kuliah = serializers.CharField(max_length=100)
    
    def validate_nim(self, value):
        try:
            user = User.objects.get(username=value, role='mahasiswa')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Mahasiswa dengan NIM tersebut tidak ditemukan")
    
    def create(self, validated_data):
        nim = validated_data['nim']
        mata_kuliah = validated_data['mata_kuliah']
        
        user = User.objects.get(username=nim, role='mahasiswa')
        
        # Check if attendance already exists for today
        today = datetime.now().date()
        existing_attendance = Attendance.objects.filter(
            nim=nim, 
            mata_kuliah=mata_kuliah, 
            tanggal=today
        ).first()
        
        if existing_attendance:
            raise serializers.ValidationError("Mahasiswa sudah absen untuk mata kuliah ini hari ini")
        
        attendance = Attendance.objects.create(
            nim=nim,
            nama=user.first_name or user.username,
            mata_kuliah=mata_kuliah,
            tanggal=datetime.now().date(),
            waktu=datetime.now().time(),
            status='Hadir',
            recorded_by=self.context['request'].user
        )
        
        return attendance

class AttendanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['tanggal', 'mata_kuliah', 'status']

class LecturerAttendanceViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['nim', 'nama', 'mata_kuliah', 'tanggal', 'status']