## run a project:

```PYTHONPATH=src uvicorn src.main:app --reload```

# Document Backend

A comprehensive backend system for document management, data extraction, and authentication built with FastAPI, SQLite, and Poetry.

## Features

- **Authentication System**
    - JWT-based authentication with access and refresh tokens
    - Role-based access control
    - User management (create, update, delete)
    - Token revocation and refresh

- **Document Management**
    - Upload and retrieve documents
    - Document metadata handling
    - Multi-tenant support

- **Data Extraction**
    - OCR-based extraction (simulated)
    - LLM-based extraction (simulated)
    - Hybrid extraction approaches
    - Background processing of extraction jobs

- **Search Capabilities**
    - Document search with filters
    - Extraction data search
    - Hybrid search across documents and extractions

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - ORM for SQL databases with Python type annotations
- **SQLite** - Lightweight disk-based database
- **Poetry** - Dependency management and packaging
- **Pydantic** - Data validation and settings management
- **Jose/JWT** - JSON Web Tokens for authentication
- **Passlib/Bcrypt** - Password hashing and verification
- **Uvicorn** - ASGI server for FastAPI

## Project Structure

```
document-central/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── core/                    # Core application functionality
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── security.py          # Security utilities
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── users.py             # User management endpoints
│   │   ├── documents.py         # Document management endpoints
│   │   ├── extracts.py          # Data extraction endpoints
│   │   └── search.py            # Search endpoints
│   ├── db/                      # Database configuration
│   │   ├── __init__.py
│   │   ├── database.py          # Database setup
│   │   └── init_db.py           # Database initialization
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── user.py              # User models
│   │   ├── token.py             # Token models
│   │   ├── document.py          # Document models
│   │   └── extract.py           # Extraction models
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   └── extraction.py        # Extraction service
│   └── providers/               # Provider implementations
│       ├── __init__.py
│       ├── auth_provider.py     # Authentication provider
│       └── tenant_provider.py   # Tenant management provider
├── docroot/                     # Document storage directory
├── migrations/                  # Database migrations
├── tests/                       # Test suite
├── .env.example                 # Example environment variables
├── pyproject.toml              # Poetry configuration
└── README.md                    # Project documentation
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- Poetry package manager

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/document-central.git
   ```

2. **Install Poetry** (if not already installed)

   ```bash
   # Linux/macOS/WSL
   curl -sSL https://install.python-poetry.org | python3 -

   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. **Set up environment**

   ```bash
   # Create .env file from template
   cp .env.example .env
   
   # Generate a random secret key
   echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env
   ```

4. **Install dependencies**

   ```bash
   poetry install
   ```

5. **Activate the virtual environment**

   ```bash
   poetry shell
   ```

6. **Create required directories**

   ```bash
   mkdir -p docroot
   ```

7. **Run the application**

   ```bash
   python -m app.main
   ```

   The API will be available at http://localhost:8000
   API documentation will be available at http://localhost:8000/docs

## First-time Setup

After starting the application, you'll need to create your first admin user:

1. Create a regular user through the API (POST /api/v1/users/)
2. Then update the user's role to include "ADMIN" using SQLite directly:

```bash
sqlite3 project.db
```

```sql
UPDATE user SET roles = 'ADMIN,USER' WHERE id = 1;
```

## API Endpoints

### Authentication

- **POST /api/v1/auth/login** - Login with username/password
- **POST /api/v1/auth/refresh** - Refresh access token
- **GET /api/v1/auth/me** - Get current user info
- **POST /api/v1/auth/logout** - Logout and revoke refresh token

### User Management

- **GET /api/v1/users/** - List all users (admin only)
- **POST /api/v1/users/** - Create a new user (admin only)
- **GET /api/v1/users/{user_id}** - Get user details
- **PUT /api/v1/users/{user_id}** - Update a user
- **DELETE /api/v1/users/{user_id}** - Delete a user (admin only)
- **PUT /api/v1/users/{user_id}/roles** - Update user roles (admin only)

### Data Extraction

- **GET /api/v1/extracts/** - List all extractions
- **POST /api/v1/extracts/** - Create a new extraction job
- **GET /api/v1/extracts/{extract_id}** - Get extraction details
- **PUT /api/v1/extracts/{extract_id}** - Update extraction data
- **DELETE /api/v1/extracts/{extract_id}** - Delete an extraction
- **POST /api/v1/extracts/document/{document_id}** - Create extraction for document

### Search

- **GET /api/v1/search/documents** - Search documents with filters
- **GET /api/v1/search/extracts** - Search extractions with filters
- **GET /api/v1/search/hybrid** - Hybrid search across documents and extractions

## Authentication Flow

1. **Login**:
   ```http
   POST /api/v1/auth/login
   Content-Type: application/x-www-form-urlencoded

   username=admin&password=password
   ```

   Response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "a1b2c3d4e5f6...",
     "expires_in": 1800,
     "token_type": "bearer",
     "user_id": 1,
     "username": "admin",
     "roles": ["ADMIN", "USER"]
   }
   ```

2. **Use Access Token**:
   ```http
   GET /api/v1/auth/me
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. **Refresh Token**:
   ```http
   POST /api/v1/auth/refresh
   Content-Type: application/json

   {
     "refresh_token": "a1b2c3d4e5f6..."
   }
   ```

4. **Logout**:
   ```http
   POST /api/v1/auth/logout
   Content-Type: application/json
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   {
     "refresh_token": "a1b2c3d4e5f6..."
   }
   ```

## Upload and Extraction Flow

1. **Upload a Document**:
   ```http
   POST /api/v1/documents/
   Content-Type: multipart/form-data
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   file=@invoice.pdf
   document_class=invoice
   document_type=billing
   metadata={"customer": "ACME Corp", "invoice_number": "INV-12345"}
   ```

2. **Start Extraction**:
   ```http
   POST /api/v1/extracts/document/abc123def456
   Content-Type: application/json
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   {
     "strategy": "hybrid"
   }
   ```

3. **Check Extraction Status**:
   ```http
   GET /api/v1/extracts/xyz789abc012
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Get Extraction Data**:
   ```
   Same as above, but once status is "completed"
   ```

## Role-Based Access Control

The system supports role-based access control with the following roles:

- **USER** - Basic access to documents and extractions
- **ADMIN** - Administrative access for user management

Users can have multiple roles (comma-separated in the database).

## Multi-Tenant Support

The system is designed to support multiple tenants:

- Each user belongs to a tenant
- Documents and extractions are associated with tenants
- Users can only access resources within their own tenant

## Configuration

The application can be configured using environment variables or a .env file:

|
Variable
|
Description
|
Default
|
|
----------
|
-------------
|
---------
|
|
API_V1_STR
|
API version prefix
|
"/api/v1"
|
|
PROJECT_NAME
|
Project name
|
"Auth API"
|
|
SECRET_KEY
|
JWT secret key
|
auto-generated
|
|
ALGORITHM
|
JWT algorithm
|
"HS256"
|
|
ACCESS_TOKEN_EXPIRE_MINUTES
|
Access token lifetime
|
30
|
|
REFRESH_TOKEN_EXPIRE_DAYS
|
Refresh token lifetime
|
7
|
|
DATABASE_URL
|
Database connection string
|
"sqlite:///./project.db"
|
|
BACKEND_CORS_ORIGINS
|
Allowed CORS origins
|
["http://localhost:4200"]
|

## Angular Integration

This backend is designed to work with an Angular frontend. Update your frontend authentication service to use the new endpoints:

```typescript
// auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    return this.http.post(`${this.apiUrl}/auth/login`, formData);
  }

  refreshToken(refreshToken: string): Observable {
    return this.http.post(`${this.apiUrl}/auth/refresh`, { refresh_token: refreshToken });
  }

  logout(refreshToken: string): Observable {
    return this.http.post(`${this.apiUrl}/auth/logout`, { refresh_token: refreshToken });
  }

  getProfile(): Observable {
    return this.http.get(`${this.apiUrl}/auth/me`);
  }
}
```

## Development Guidelines

### Adding a New Model

1. Create a new file in the `app/models/` directory
2. Define SQLModel classes for database and API schemas
3. Add the model to `app/db/init_db.py` for table creation

### Adding a New API Endpoint

1. Create or modify a router file in the `app/api/` directory
2. Define the endpoint function with appropriate dependencies
3. Include the router in `app/main.py`

### Authentication and Authorization

Always use the appropriate dependency to ensure authentication:

```python
from app.core.dependencies import get_current_active_user

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": "This is protected", "user": current_user.username}
```

For role-based authorization:

```python
from app.api.deps import check_roles

@router.get("/admin-only")
async def admin_route(
    current_user: User = Depends(check_roles(["ADMIN"]))
):
    return {"message": "Admin access granted", "user": current_user.username}
```

## Testing

Run tests using pytest:

```bash
poetry run pytest
```

## Deployment

### Docker Deployment

A Dockerfile is provided for containerized deployment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.5.1

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY app ./app

# Configure Poetry to not use virtual environments in Docker
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Create required directories
RUN mkdir -p docroot

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run the Docker container:

```bash
docker build -t document-central:latest .
docker run -p 8000:8000 document-central:latest
```

### Production Considerations

For production deployment, consider the following:

- Use a production-grade database (PostgreSQL, MySQL)
- Set up proper SSL/TLS termination
- Implement a robust backup strategy
- Configure appropriate logging
- Set up monitoring and alerting
- Use container orchestration (Kubernetes, Docker Swarm)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.