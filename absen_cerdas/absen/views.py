from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import login
from django.utils.crypto import get_random_string
from datetime import datetime
import string
import cv2
import numpy as np
from PIL import Image
from django.utils import timezone

from .models import User, Attendance
from .serializers import (
    LoginSerializer, 
    AttendanceCreateSerializer, 
    AttendanceHistorySerializer,
    LecturerAttendanceViewSerializer
)

def generate_token():
    """Generate a simple token for authentication"""
    return get_random_string(32)

class LoginAPIView(APIView):
    """Handle user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate token (in production, use proper JWT tokens)
            token = generate_token()
            
            # Store token and creation time
            user.token = token
            user.token_created = timezone.now()
            user.save()
            
            # Determine navigation screen based on user role
            if user.role == 'mahasiswa':
                navigation_screen = 'mahasiswa_screen'
            elif user.role == 'dosen':
                navigation_screen = 'dosen_screen'
            else:
                navigation_screen = 'mahasiswa_screen'  # Default fallback
            
            response_data = {
                "success": True,
                "message": "Login berhasil",
                "data": {
                    "id": user.id,
                    "nama": user.first_name or user.username,
                    "role": user.role,
                    "token": token,
                    "navigation_screen": navigation_screen
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "User tidak ditemukan"
            }, status=status.HTTP_400_BAD_REQUEST)

class AttendanceAPIView(APIView):
    """Handle student attendance"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AttendanceCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            attendance = serializer.save()
            
            response_data = {
                "success": True,
                "message": "Absen berhasil",
                "data": {
                    "tanggal": attendance.tanggal.strftime('%Y-%m-%d'),
                    "waktu": attendance.waktu.strftime('%H:%M:%S'),
                    "status": attendance.status
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": str(serializer.errors)
            }, status=status.HTTP_400_BAD_REQUEST)

class AttendanceHistoryAPIView(APIView):
    """Handle student attendance history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        nim = request.query_params.get('nim')
        
        if not nim:
            return Response({
                "success": False,
                "message": "Parameter NIM diperlukan"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the requesting user has permission to view this history
        if request.user.role == 'mahasiswa' and request.user.username != nim:
            return Response({
                "success": False,
                "message": "Anda tidak memiliki akses untuk melihat riwayat absen mahasiswa lain"
            }, status=status.HTTP_403_FORBIDDEN)
        
        attendances = Attendance.objects.filter(nim=nim)
        serializer = AttendanceHistorySerializer(attendances, many=True)
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class LecturerAttendanceAPIView(APIView):
    """Handle lecturer attendance view"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Only lecturers can access this endpoint
        if request.user.role != 'dosen':
            return Response({
                "success": False,
                "message": "Akses ditolak. Hanya dosen yang dapat mengakses endpoint ini."
            }, status=status.HTTP_403_FORBIDDEN)
        
        attendances = Attendance.objects.all()
        serializer = LecturerAttendanceViewSerializer(attendances, many=True)
        
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AIFaceValidationAPIView(APIView):
    """Handle AI face validation for attendance"""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Check if image file is provided
        if 'foto' not in request.FILES:
            return Response({
                "success": False,
                "message": "File foto diperlukan",
                "ai_result": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['foto']
        
        try:
            # Read image from uploaded file
            image_data = image_file.read()
            
            # Convert to PIL Image then to numpy array
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert PIL Image to numpy array (OpenCV format)
            img_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Load the pre-trained face cascade classifier
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Detect faces in the image
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Calculate confidence based on face detection
            if len(faces) == 0:
                # No face detected
                confidence = 0.0
                is_valid = False
            else:
                # Face detected - calculate confidence based on face size and position
                # Get the largest face (assumed to be the main subject)
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                
                # Calculate confidence based on:
                # 1. Face size relative to image (larger = better)
                # 2. Face position (centered = better)
                # 3. Number of faces detected (single face = better)
                
                img_height, img_width = gray.shape
                face_area = w * h
                image_area = img_width * img_height
                
                # Size score (0.0 to 0.4) - face should be at least 5% of image
                size_ratio = face_area / image_area
                size_score = min(size_ratio * 8, 0.4)  # Max 0.4
                
                # Position score (0.0 to 0.3) - face should be centered
                face_center_x = x + w / 2
                face_center_y = y + h / 2
                center_x = img_width / 2
                center_y = img_height / 2
                
                distance_from_center = np.sqrt(
                    ((face_center_x - center_x) / img_width) ** 2 + 
                    ((face_center_y - center_y) / img_height) ** 2
                )
                position_score = max(0.3 - distance_from_center, 0)
                
                # Single face bonus (0.0 to 0.3)
                single_face_score = 0.3 if len(faces) == 1 else 0.15
                
                # Calculate final confidence
                confidence = size_score + position_score + single_face_score
                confidence = min(max(confidence, 0.0), 1.0)  # Clamp to 0-1
                
                # Round to 2 decimal places
                confidence = round(confidence, 2)
                
                # Determine validity based on threshold
                is_valid = confidence >= 0.7
            
            # Prepare response
            if is_valid:
                return Response({
                    "success": True,
                    "ai_result": {
                        "status": "Valid",
                        "confidence": confidence
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "ai_result": {
                        "status": "Tidak Valid",
                        "confidence": confidence
                    }
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error processing image: {str(e)}",
                "ai_result": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
