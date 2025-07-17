"""
Green PM - Main API Router
"""
from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth,
    users,
    properties,
    leases,
    payments,
    maintenance,
    messages,
    applications,
    admin,
    files
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(leases.router, prefix="/leases", tags=["Leases"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])