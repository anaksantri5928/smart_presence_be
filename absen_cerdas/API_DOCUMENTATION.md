# Attendance System API Documentation

## Overview
This is the API documentation for the Smart Attendance System with AI face validation features.

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication
The system uses token-based authentication. Tokens are generated during login and should be included in the Authorization header for protected endpoints.

```
Authorization: Token <your_token_here>
```

## API Endpoints

### 1. POST /api/login/ - User Login

**Description**: Authenticate user and receive navigation screen based on role

**Request**:
```json
{
  "username": "2021001",
  "password": "password123"
}
```

**Response - Success**:
```json
{
  "success": true,
  "message": "Login berhasil",
  "data": {
    "id": 1,
    "nama": "John Doe",
    "role": "mahasiswa",
    "token": "generated_token_here",
    "navigation_screen": "mahasiswa_screen"
  }
}
```

**Navigation Screen Mapping**:
- `mahasiswa` role → `mahasiswa_screen`
- `dosen` role → `dosen_screen`
- Dashboard screen has been removed

---

### 2. POST /api/ai/validate/ - AI Face Validation

**Description**: Validate uploaded photo for attendance using AI face detection

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Body: `foto` field containing image file

**Response - Valid Face** (confidence ≥ 0.7):
```json
{
  "success": true,
  "ai_result": {
    "status": "Valid",
    "confidence": 0.85
  }
}
```

**Response - Invalid Face** (confidence < 0.7):
```json
{
  "success": false,
  "ai_result": {
    "status": "Tidak Valid",
    "confidence": 0.3
  }
}
```

**Response - Error** (no file):
```json
{
  "success": false,
  "message": "File foto diperlukan",
  "ai_result": null
}
```

**AI Validation Rules**:
- Uses OpenCV's Haar Cascade classifier for face detection
- Confidence calculated based on:
  - Face size relative to image (0-0.4 points)
  - Face centeredness (0-0.3 points)
  - Single face preference (0.15-0.3 points)
- Valid if total confidence ≥ 0.7

---

### 3. POST /api/absen/ - Submit Attendance

**Description**: Submit student attendance (requires authentication)

**Request**:
```json
{
  "nim": "2021001",
  "foto": "base64_encoded_image_or_file_upload"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Absen berhasil",
  "data": {
    "tanggal": "2025-12-30",
    "waktu": "15:30:45",
    "status": "Hadir"
  }
}
```

---

### 4. GET /api/absen/riwayat/ - Get Attendance History

**Description**: Get student attendance history (requires authentication)

**Request**:
```
GET /api/absen/riwayat/?nim=2021001
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "nim": "2021001",
      "tanggal": "2025-12-30",
      "waktu": "15:30:45",
      "status": "Hadir"
    }
  ]
}
```

---

### 5. GET /api/dosen/absen/ - Lecturer Attendance View

**Description**: Get all attendance records (lecturer only, requires authentication)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "nim": "2021001",
      "nama": "John Doe",
      "tanggal": "2025-12-30",
      "waktu": "15:30:45",
      "status": "Hadir"
    }
  ]
}
```

## Error Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Server error during processing

## Dependencies

Required Python packages:
```bash
pip install opencv-python numpy pillow django djangorestframework
```

## Testing

### Test Login Navigation
```bash
cd absen_cerdas
python test_login_navigation.py
```

### Test AI Validation
```bash
cd absen_cerdas
python test_ai_validation.py
```

### Manual Testing with curl

**Login**:
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"2021001","password":"password123"}'
```

**AI Validation**:
```bash
curl -X POST http://127.0.0.1:8000/api/ai/validate/ \
  -F "foto=@path_to_your_image.jpg"
```

## Integration Notes

1. **Login Flow**: Frontend should read `navigation_screen` from login response and navigate accordingly
2. **AI Validation**: Should be called before attendance submission for quality assurance
3. **Error Handling**: All endpoints return consistent error format
4. **Token Management**: Tokens should be stored securely and refreshed as needed