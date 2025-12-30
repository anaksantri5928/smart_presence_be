#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('f:/CODE/joki absen cerdas/absen_cerdas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'absen_cerdas.settings')
django.setup()

from absen.models import User

def create_test_users():
    # Create test students
    try:
        User.objects.create_user(username='2021001', password='password123', role='mahasiswa', first_name='Andi', nim='2021001')
        print("Created student: 2021001 (Andi)")
    except Exception as e:
        print(f"Error creating student 2021001: {e}")
    
    # try:
    #     User.objects.create_user(username='2021002', password='password123', role='mahasiswa', first_name='Budi', nim='2021002')
    #     print("Created student: 2021002 (Budi)")
    # except Exception as e:
    #     print(f"Error creating student 2021002: {e}")
    
    # Create test lecturer
    try:
        User.objects.create_user(username='D001', password='password123', role='dosen', first_name='Dr. Susi', nidn='D001')
        print("Created lecturer: D001 (Dr. Susi)")
    except Exception as e:
        print(f"Error creating lecturer D001: {e}")
    
    print("Test users creation completed!")

if __name__ == "__main__":
    create_test_users()