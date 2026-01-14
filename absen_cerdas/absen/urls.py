from django.urls import path
from .views import (
    LoginView, FaceEnrollView, AttendanceCheckinView, AttendanceHistoryView,
    ClassCreateView, ClassMyView, ClassListView, AttendanceRecapView
)

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='login'),
    path('face/enroll', FaceEnrollView.as_view(), name='face_enroll'),
    path('attendance/checkin', AttendanceCheckinView.as_view(), name='attendance_checkin'),
    path('attendance/history', AttendanceHistoryView.as_view(), name='attendance_history'),
    path('classes', ClassCreateView.as_view(), name='class_create'),
    path('classes/my', ClassMyView.as_view(), name='class_my'),
    path('classes/list', ClassListView.as_view(), name='class_list'),
    path('attendance/recap/<int:class_id>', AttendanceRecapView.as_view(), name='attendance_recap'),
]