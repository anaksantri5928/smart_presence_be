from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import User, FaceEmbedding, Attendance, Class
from .serializers import (
    LoginSerializer, FaceEnrollSerializer, CheckinSerializer, UserSerializer,
    ClassSerializer, ClassListSerializer, AttendanceHistorySerializer,
    AttendanceRecapSerializer
)
from .authentication import generate_token
from .face_utils import extract_embedding, enroll_with_multiple_images, verify_face

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    token = generate_token(user)
                    return Response({
                        'status': True,
                        'message': 'Login berhasil',
                        'data': UserSerializer(user).data,
                        'token': token
                    })
                else:
                    return Response({
                        'status': False,
                        'message': 'Password salah'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({
                    'status': False,
                    'message': 'Username tidak ditemukan'
                }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FaceEnrollView(APIView):
    def post(self, request):
        if request.user.role != 'mahasiswa':
            return Response({
                'status': False,
                'message': 'Hanya mahasiswa yang dapat enroll wajah'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = FaceEnrollSerializer(data=request.data)
        if serializer.is_valid():
            images = serializer.validated_data['images']

            # Check if already enrolled
            if FaceEmbedding.objects.filter(user=request.user).exists():
                return Response({
                    'status': False,
                    'message': 'Wajah sudah terdaftar'
                }, status=status.HTTP_400_BAD_REQUEST)

            embedding = enroll_with_multiple_images(images)
            if embedding is None:
                return Response({
                    'status': False,
                    'message': 'Gagal mendeteksi wajah pada gambar yang diupload'
                }, status=status.HTTP_400_BAD_REQUEST)

            FaceEmbedding.objects.create(user=request.user, embedding=embedding)

            return Response({
                'status': True,
                'message': 'Wajah berhasil didaftarkan',
                'data': {
                    'user_id': request.user.id,
                    'images_used': len(images)
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceHistoryView(APIView):
    def get(self, request):
        if request.user.role != 'mahasiswa':
            return Response({
                'status': False,
                'message': 'Hanya mahasiswa yang dapat melihat histori absensi'
            }, status=status.HTTP_403_FORBIDDEN)

        attendances = Attendance.objects.filter(user=request.user).order_by('-timestamp')
        serializer = AttendanceHistorySerializer(attendances, many=True)

        return Response({
            'status': True,
            'message': 'Histori absensi',
            'data': serializer.data
        })

class ClassCreateView(APIView):
    def post(self, request):
        if request.user.role != 'dosen':
            return Response({
                'status': False,
                'message': 'Hanya dosen yang dapat membuat kelas'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ClassSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            class_obj = serializer.save()
            return Response({
                'status': True,
                'message': 'Kelas berhasil dibuat',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClassMyView(APIView):
    def get(self, request):
        if request.user.role == 'dosen':
            # Dosen melihat semua kelas yang dibuatnya
            classes = Class.objects.filter(lecturer=request.user)
            message = 'Daftar kelas yang Anda buat'
        else:
            # Mahasiswa melihat semua kelas yang tersedia
            classes = Class.objects.all()
            message = 'Daftar kelas yang tersedia'

        serializer = ClassListSerializer(classes, many=True)

        return Response({
            'status': True,
            'message': message,
            'data': serializer.data
        })

class ClassListView(APIView):
    def get(self, request):
        if request.user.role == 'dosen':
            classes = Class.objects.filter(lecturer=request.user)
        else:
            classes = Class.objects.all()

        serializer = ClassListSerializer(classes, many=True)

        return Response({
            'status': True,
            'message': 'Daftar kelas',
            'data': serializer.data
        })

class AttendanceRecapView(APIView):
    def get(self, request, class_id):
        if request.user.role != 'dosen':
            return Response({
                'status': False,
                'message': 'Hanya dosen yang dapat melihat rekap absensi'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            class_obj = Class.objects.get(id=class_id, lecturer=request.user)
        except Class.DoesNotExist:
            return Response({
                'status': False,
                'message': 'Kelas tidak ditemukan atau bukan milik Anda'
            }, status=status.HTTP_404_NOT_FOUND)

        attendances = Attendance.objects.filter(class_id=class_obj).select_related('user')
        total_mahasiswa = User.objects.filter(role='mahasiswa').count()
        total_hadir = attendances.count()

        attendance_data = []
        for attendance in attendances:
            attendance_data.append({
                'mahasiswa': UserSerializer(attendance.user).data,
                'confidence': attendance.confidence,
                'timestamp': attendance.timestamp
            })

        return Response({
            'status': True,
            'message': 'Rekap absensi kelas',
            'data': {
                'class': ClassListSerializer(class_obj).data,
                'total_mahasiswa': total_mahasiswa,
                'total_hadir': total_hadir,
                'absensi': attendance_data
            }
        })

class AttendanceCheckinView(APIView):
    def post(self, request):
        serializer = CheckinSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            class_id = serializer.validated_data['class_id']

            try:
                class_obj = Class.objects.get(id=class_id)
            except Class.DoesNotExist:
                return Response({
                    'status': False,
                    'message': 'Kelas tidak ditemukan'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get user's embedding
            try:
                face_embedding = FaceEmbedding.objects.get(user=request.user)
            except FaceEmbedding.DoesNotExist:
                return Response({
                    'status': False,
                    'message': 'Wajah belum terdaftar'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Extract embedding from checkin image
            checkin_emb = extract_embedding(image)
            if checkin_emb is None:
                return Response({
                    'status': False,
                    'message': 'Wajah tidak terdeteksi pada gambar check-in'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verify
            is_valid, confidence = verify_face(face_embedding.embedding, checkin_emb)

            if is_valid:
                Attendance.objects.create(
                    user=request.user,
                    class_id=class_obj,
                    confidence=confidence
                )
                return Response({
                    'status': True,
                    'message': 'Absensi berhasil',
                    'data': {
                        'class_id': class_id,
                        'confidence': round(confidence, 3)
                    }
                })
            else:
                return Response({
                    'status': False,
                    'message': 'Wajah tidak cocok',
                    'data': {
                        'confidence': round(confidence, 3)
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)