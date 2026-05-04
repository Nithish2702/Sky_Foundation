# Qatar Foundation Admin Portal - Backend

Backend API for the Qatar Foundation Admin Portal built with Python and Flask.

## Features

### Task 1 - Authentication (Day 1)
- ✅ **US-1.1**: Admin Sign Up with validation
- ✅ **US-1.2**: Admin Login with Remember Me functionality
- ✅ **US-1.3**: Forgot Password with secure token generation

### Task 2 - Opportunity Management (Day 2)
- ✅ **US-2.1**: View All Opportunities (admin-specific)
- ✅ **US-2.2**: Add New Opportunity with validation
- ✅ **US-2.3**: Opportunities Persist After Login
- ✅ **US-2.4**: View Opportunity Details
- ✅ **US-2.5**: Edit an Opportunity
- ✅ **US-2.6**: Delete an Opportunity with confirmation

## Tech Stack

- **Framework**: Flask 3.0.0
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Session-based with secure password hashing
- **CORS**: Flask-CORS for frontend integration

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── qatar_foundation.db   # SQLite database (created on first run)
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication

#### Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@qf.org.qa",
  "password": "password123",
  "confirm_password": "password123"
}
```

**Response (201 Created)**
```json
{
  "message": "Account created successfully",
  "admin": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@qf.org.qa"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@qf.org.qa",
  "password": "password123",
  "remember_me": true
}
```

**Response (200 OK)**
```json
{
  "message": "Login successful",
  "admin": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@qf.org.qa"
  }
}
```

#### Logout
```http
POST /api/auth/logout
```

**Response (200 OK)**
```json
{
  "message": "Logged out successfully"
}
```

#### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "john@qf.org.qa"
}
```

**Response (200 OK)**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent"
}
```

#### Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-here",
  "new_password": "newpassword123"
}
```

**Response (200 OK)**
```json
{
  "message": "Password reset successfully"
}
```

#### Get Current Admin
```http
GET /api/auth/me
```

**Response (200 OK)**
```json
{
  "admin": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@qf.org.qa",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### Opportunities

#### Get All Opportunities
```http
GET /api/opportunities
```

**Response (200 OK)**
```json
{
  "opportunities": [
    {
      "id": 1,
      "admin_id": 1,
      "name": "Full Stack Web Development",
      "duration": "6 Months",
      "start_date": "2026-02-01",
      "description": "Comprehensive program...",
      "skills": "HTML, CSS, JavaScript, React",
      "skills_list": ["HTML", "CSS", "JavaScript", "React"],
      "category": "technology",
      "future_opportunities": "Career paths include...",
      "max_applicants": 100,
      "current_applicants": 0,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

#### Create Opportunity
```http
POST /api/opportunities
Content-Type: application/json

{
  "name": "Full Stack Web Development",
  "duration": "6 Months",
  "start_date": "2026-02-01",
  "description": "Comprehensive program covering HTML, CSS, JavaScript...",
  "skills": "HTML, CSS, JavaScript, React, Node.js",
  "category": "technology",
  "future_opportunities": "Graduates can pursue roles as Full Stack Developers...",
  "max_applicants": 100
}
```

**Response (201 Created)**
```json
{
  "message": "Opportunity created successfully",
  "opportunity": {
    "id": 1,
    "name": "Full Stack Web Development",
    ...
  }
}
```

#### Get Opportunity Details
```http
GET /api/opportunities/{id}
```

**Response (200 OK)**
```json
{
  "opportunity": {
    "id": 1,
    "name": "Full Stack Web Development",
    ...
  }
}
```

#### Update Opportunity
```http
PUT /api/opportunities/{id}
Content-Type: application/json

{
  "name": "Updated Opportunity Name",
  "duration": "8 Months",
  ...
}
```

**Response (200 OK)**
```json
{
  "message": "Opportunity updated successfully",
  "opportunity": {
    "id": 1,
    ...
  }
}
```

#### Delete Opportunity
```http
DELETE /api/opportunities/{id}
```

**Response (200 OK)**
```json
{
  "message": "Opportunity deleted successfully"
}
```

## Database Schema

### Admin Table
- `id`: Integer (Primary Key)
- `full_name`: String(100)
- `email`: String(120) - Unique, Indexed
- `password_hash`: String(255)
- `created_at`: DateTime
- `last_login`: DateTime

### Opportunity Table
- `id`: Integer (Primary Key)
- `admin_id`: Integer (Foreign Key → admins.id)
- `name`: String(200)
- `duration`: String(50)
- `start_date`: String(50)
- `description`: Text
- `skills`: Text (comma-separated)
- `category`: String(50)
- `future_opportunities`: Text
- `max_applicants`: Integer (nullable)
- `current_applicants`: Integer (default: 0)
- `created_at`: DateTime
- `updated_at`: DateTime

### PasswordResetToken Table
- `id`: Integer (Primary Key)
- `admin_id`: Integer (Foreign Key → admins.id)
- `token`: String(255) - Unique, Indexed
- `expires_at`: DateTime
- `used`: Boolean (default: False)
- `created_at`: DateTime

## Security Features

1. **Password Hashing**: Uses Werkzeug's secure password hashing
2. **Session Management**: Secure session-based authentication
3. **CSRF Protection**: Built-in Flask session protection
4. **Email Privacy**: Generic error messages to prevent email enumeration
5. **Token Expiration**: Password reset tokens expire after 1 hour
6. **Input Validation**: Comprehensive validation on all endpoints
7. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `404`: Not Found
- `409`: Conflict (duplicate email)
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "error": "Error message here"
}
```

## Testing the API

### Using cURL

**Sign Up**
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@qf.org.qa","password":"password123","confirm_password":"password123"}'
```

**Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"john@qf.org.qa","password":"password123","remember_me":true}'
```

**Create Opportunity**
```bash
curl -X POST http://localhost:5000/api/opportunities \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"Test Opportunity","duration":"3 Months","start_date":"2026-03-01","description":"Test description","skills":"Skill1, Skill2","category":"technology","future_opportunities":"Career paths...","max_applicants":50}'
```

### Using Postman

1. Import the API endpoints
2. For authenticated requests, ensure cookies are enabled
3. Login first to establish a session
4. Use the session cookie for subsequent requests

## Development Notes

- The database is automatically created on first run
- Session data is stored in the filesystem (Flask-Session)
- Password reset links are logged to console (no email sending in development)
- CORS is configured to allow requests from common development origins

## Production Deployment

Before deploying to production:

1. **Change SECRET_KEY**: Use a strong, random secret key
2. **Use PostgreSQL**: Replace SQLite with PostgreSQL for production
3. **Enable HTTPS**: Set `SESSION_COOKIE_SECURE = True`
4. **Configure Email**: Implement actual email sending for password resets
5. **Set Environment Variables**: Use environment variables for all sensitive data
6. **Enable Logging**: Add proper logging for monitoring
7. **Rate Limiting**: Add rate limiting to prevent abuse
8. **CORS Configuration**: Restrict CORS to your frontend domain only

## Support

For issues or questions, please refer to the project documentation or contact the development team.
