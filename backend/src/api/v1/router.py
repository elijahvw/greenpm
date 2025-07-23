"""
Green PM - Main API Router
"""
from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth, 
    simple_auth,
    users, 
    properties, 
    applications, 
    leases, 
    maintenance, 
    payments_simple as payments, 
    messages, 
    admin,
    dashboard
)

api_router = APIRouter()

# Authentication & User Management
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(simple_auth.router, prefix="/auth", tags=["Simple Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Property Management
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(leases.router, prefix="/leases", tags=["Leases"])

# Operations
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])

# Admin
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])