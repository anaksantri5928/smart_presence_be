#!/usr/bin/env python3
"""
Test script for AI face validation endpoint
"""

import requests
import json

def test_ai_validation():
    """Test the AI face validation endpoint"""
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/ai/validate/"
    
    # Test data - you can replace with a real image file
    # This is just a test with no image file
    print("Testing AI validation endpoint...")
    
    # Test 1: No file provided (should fail)
    print("\nTest 1: No file provided")
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: With actual image file (you need to provide a real image)
    # Uncomment and modify the following lines to test with a real image
    """
    print("\nTest 2: With image file")
    with open('path_to_your_image.jpg', 'rb') as img_file:
        files = {'foto': img_file}
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    """

if __name__ == "__main__":
    test_ai_validation()