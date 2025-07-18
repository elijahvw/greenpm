"""
Green PM - Working Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os

# Import working API endpoints
from src.api.v1.endpoints.auth_working import router as auth_router
from src.api.v1.endpoints.properties_working import router as properties_router
from src.api.v1.endpoints.users_working import router as users_router
from src.api.v1.endpoints.maintenance_working import router as maintenance_router
from src.api.v1.endpoints.leases_working import router as leases_router
from src.api.v1.endpoints.payments_working import router as payments_router

# Initialize database
from src.core.database_simple import db

# Create FastAPI app
app = FastAPI(
    title="Green PM API",
    description="Property Management SaaS Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Green PM API is running"}

# API info endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Green PM Property Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/api/v1/auth",
            "properties": "/api/v1/properties",
            "users": "/api/v1/users",
            "maintenance": "/api/v1/maintenance",
            "leases": "/api/v1/leases",
            "payments": "/api/v1/payments"
        }
    }

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(properties_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(maintenance_router, prefix="/api/v1")
app.include_router(leases_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")

# Dashboard stats endpoint
@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Total counts
    total_users = db.execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1")[0]['count']
    total_properties = db.execute_query("SELECT COUNT(*) as count FROM properties WHERE is_active = 1")[0]['count']
    total_leases = db.execute_query("SELECT COUNT(*) as count FROM leases WHERE status = 'active'")[0]['count']
    total_maintenance = db.execute_query("SELECT COUNT(*) as count FROM maintenance_requests")[0]['count']
    
    # Revenue
    total_revenue = db.execute_query("SELECT SUM(amount) as total FROM payments WHERE status = 'completed'")[0]['total'] or 0
    
    # Recent activity
    recent_users = db.execute_query("""
        SELECT COUNT(*) as count FROM users 
        WHERE created_at >= date('now', '-30 days') AND is_active = 1
    """)[0]['count']
    
    recent_properties = db.execute_query("""
        SELECT COUNT(*) as count FROM properties 
        WHERE created_at >= date('now', '-30 days') AND is_active = 1
    """)[0]['count']
    
    recent_maintenance = db.execute_query("""
        SELECT COUNT(*) as count FROM maintenance_requests 
        WHERE created_at >= date('now', '-30 days')
    """)[0]['count']
    
    return {
        "totals": {
            "users": total_users,
            "properties": total_properties,
            "leases": total_leases,
            "maintenance_requests": total_maintenance,
            "revenue": total_revenue
        },
        "recent": {
            "users": recent_users,
            "properties": recent_properties,
            "maintenance_requests": recent_maintenance
        }
    }

# Run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "src.main_working:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )