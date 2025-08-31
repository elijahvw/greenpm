# Green PM - Demo Login Credentials

## 🔑 Demo User Accounts

### Admin Account
- **Email**: `admin@greenpm.com`
- **Password**: `GreenPM2024!`
- **Role**: Administrator
- **Access**: Full system access, user management, settings

### Landlord Account
- **Email**: `landlord@example.com`
- **Password**: `landlord123`
- **Role**: Landlord
- **Access**: Property management, tenant management, maintenance requests, payments

### Tenant Account
- **Email**: `tenant@example.com`
- **Password**: `tenant123`
- **Role**: Tenant
- **Access**: View lease, submit maintenance requests, make payments, view notices

## 🌐 Application URLs

- **Frontend (React)**: http://localhost:3000
- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Sample API Test

### Login Test
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "landlord@example.com",
    "password": "landlord123"
  }'
```

### Maintenance Requests Test
```bash
# Get token from login response, then:
curl "http://localhost:8000/api/v1/maintenance/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🚀 Features Available

- ✅ User Authentication & Authorization
- ✅ Property Management
- ✅ Lease Management  
- ✅ Maintenance Request System
- ✅ Payment Processing
- ✅ Dashboard & Analytics
- ✅ Messaging System
- ✅ Admin Panel

## 🔧 Development Notes

- Database: SQLite (local file)
- Frontend: React + TypeScript + Tailwind CSS
- Backend: FastAPI + Python
- Authentication: JWT tokens
- Real-time updates: WebSocket support planned