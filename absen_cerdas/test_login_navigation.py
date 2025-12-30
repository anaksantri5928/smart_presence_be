#!/usr/bin/env python3
"""
Test script to verify login navigation screens
"""

import requests
import json

def test_login_navigation():
    """Test that login returns correct navigation screens for different roles"""
    
    # API endpoint
    login_url = "http://127.0.0.1:8000/api/login/"
    
    print("Testing Login Navigation Screens...")
    print("=" * 50)
    
    # Test credentials for different roles
    test_users = [
        {
            "username": "2021001",
            "password": "password123",
            "expected_role": "mahasiswa",
            "expected_screen": "mahasiswa_screen"
        },
        {
            "username": "dosen01",
            "password": "password123",
            "expected_role": "dosen", 
            "expected_screen": "dosen_screen"
        }
    ]
    
    for user in test_users:
        print(f"\nTesting {user['username']} ({user['expected_role']})...")
        
        login_data = {
            "username": user['username'],
            "password": user['password']
        }
        
        try:
            response = requests.post(login_url, json=login_data)
            
            if response.status_code == 200:
                response_data = response.json()
                data = response_data.get('data', {})
                
                print(f"  ✅ Login successful")
                print(f"  📋 Role: {data.get('role')}")
                print(f"  🖥️  Navigation Screen: {data.get('navigation_screen')}")
                
                # Verify navigation screen matches expected
                if data.get('navigation_screen') == user['expected_screen']:
                    print(f"  ✅ Navigation screen correct!")
                else:
                    print(f"  ❌ Expected {user['expected_screen']}, got {data.get('navigation_screen')}")
                    
            else:
                print(f"  ❌ Login failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error: {e}")
    
    print("\n" + "=" * 50)
    print("Login navigation test completed!")

if __name__ == "__main__":
    test_login_navigation()