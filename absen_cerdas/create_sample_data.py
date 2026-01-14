import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absen_cerdas.settings')
django.setup()

from absen.models import User, Class

# Create sample users
mahasiswa = User.objects.create_user(
    username='mahasiswa01',
    password='123456',
    name='Andi Mahasiswa',
    role='mahasiswa'
)

dosen = User.objects.create_user(
    username='dosen01',
    password='123456',
    name='Budi Dosen',
    role='dosen'
)

# Create sample class
kelas = Class.objects.create(name='Matematika Dasar', lecturer=dosen)

print("Sample data created:")
print(f"Mahasiswa: {mahasiswa.username} - {mahasiswa.name}")
print(f"Dosen: {dosen.username} - {dosen.name}")
print(f"Class: {kelas.name} - Lecturer: {kelas.lecturer.name}")