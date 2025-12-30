from django.urls import path
from .views import (
    LoginAPIView,
    AttendanceAPIView,
    AttendanceHistoryAPIView,
    LecturerAttendanceAPIView,
    AIFaceValidationAPIView
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('absen/', AttendanceAPIView.as_view(), name='attendance'),
    path('absen/riwayat/', AttendanceHistoryAPIView.as_view(), name='attendance_history'),
    path('dosen/absen/', LecturerAttendanceAPIView.as_view(), name='lecturer_attendance'),
    path('ai/validate/', AIFaceValidationAPIView.as_view(), name='ai_face_validation'),
]