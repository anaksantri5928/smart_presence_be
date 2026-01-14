from rest_framework import serializers
from .models import User, FaceEmbedding, Attendance, Class

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class FaceEnrollSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.FileField(),
        min_length=1,
        max_length=5
    )

class CheckinSerializer(serializers.Serializer):
    image = serializers.FileField()
    class_id = serializers.IntegerField()

class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class_id = serializers.CharField(source='class_id.name')

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'class_id', 'confidence', 'timestamp']

class ClassSerializer(serializers.ModelSerializer):
    lecturer = UserSerializer(read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'lecturer', 'created_at']
        read_only_fields = ['lecturer']

    def create(self, validated_data):
        validated_data['lecturer'] = self.context['request'].user
        return super().create(validated_data)

class ClassListSerializer(serializers.ModelSerializer):
    dosen = serializers.CharField(source='lecturer.name', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'dosen']

class AttendanceHistorySerializer(serializers.ModelSerializer):
    class_info = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'class_info', 'confidence', 'timestamp']

    def get_class_info(self, obj):
        return {
            'id': obj.class_id.id,
            'name': obj.class_id.name
        }

class AttendanceRecapSerializer(serializers.Serializer):
    mahasiswa = UserSerializer()
    confidence = serializers.FloatField()
    timestamp = serializers.DateTimeField()