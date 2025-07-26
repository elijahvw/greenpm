"""
Green PM - Multi-tenant Support
"""
from typing import Optional, Dict, Any
from contextvars import ContextVar
from fastapi import Request, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.models.company import Company, CompanyStatus
from src.models.user import User, UserRole

# Context variables for tenant isolation
current_company_id: ContextVar[Optional[int]] = ContextVar('current_company_id', default=None)
current_user_id: ContextVar[Optional[int]] = ContextVar('current_user_id', default=None)
current_user_role: ContextVar[Optional[str]] = ContextVar('current_user_role', default=None)
is_platform_admin: ContextVar[bool] = ContextVar('is_platform_admin', default=False)

class TenantContext:
    """Tenant context manager for multi-tenant operations"""
    
    def __init__(self, company_id: Optional[int] = None, user_id: Optional[int] = None, 
                 user_role: Optional[str] = None, is_platform_admin: bool = False):
        self.company_id = company_id
        self.user_id = user_id
        self.user_role = user_role
        self.is_platform_admin = is_platform_admin
    
    def __enter__(self):
        self.company_token = current_company_id.set(self.company_id)
        self.user_token = current_user_id.set(self.user_id)
        self.role_token = current_user_role.set(self.user_role)
        self.admin_token = is_platform_admin.set(self.is_platform_admin)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        current_company_id.reset(self.company_token)
        current_user_id.reset(self.user_token)
        current_user_role.reset(self.role_token)
        is_platform_admin.reset(self.admin_token)

def get_current_company_id() -> Optional[int]:
    """Get the current company ID from context"""
    return current_company_id.get()

def get_current_user_id() -> Optional[int]:
    """Get the current user ID from context"""
    return current_user_id.get()

def get_current_user_role() -> Optional[str]:
    """Get the current user role from context"""
    return current_user_role.get()

def is_current_user_platform_admin() -> bool:
    """Check if current user is a platform admin"""
    return is_platform_admin.get()

async def resolve_tenant_from_subdomain(subdomain: str) -> Optional[Company]:
    """Resolve company from subdomain"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT id, name, subdomain, status, suspended_at
                FROM companies 
                WHERE subdomain = :subdomain
            """),
            {"subdomain": subdomain}
        )
        
        company_row = result.fetchone()
        if not company_row:
            return None
        
        # Check if company is active
        if company_row.status != CompanyStatus.ACTIVE:
            return None
        
        return Company(
            id=company_row.id,
            name=company_row.name,
            subdomain=company_row.subdomain,
            status=company_row.status,
            suspended_at=company_row.suspended_at
        )

async def resolve_tenant_from_user(user_id: int) -> Optional[Company]:
    """Resolve company from user ID"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""
                SELECT c.id, c.name, c.subdomain, c.status, c.suspended_at,
                       u.role
                FROM companies c
                JOIN users u ON u.company_id = c.id
                WHERE u.id = :user_id
            """),
            {"user_id": user_id}
        )
        
        row = result.fetchone()
        if not row:
            return None
        
        # Platform admins don't belong to a specific company
        if row.role == UserRole.PLATFORM_ADMIN:
            return None
        
        return Company(
            id=row.id,
            name=row.name,
            subdomain=row.subdomain,
            status=row.status,
            suspended_at=row.suspended_at
        )

def extract_subdomain_from_host(host: str) -> Optional[str]:
    """Extract subdomain from host header"""
    if not host:
        return None
    
    # Remove port if present
    host = host.split(':')[0]
    
    # Split by dots
    parts = host.split('.')
    
    # For development (localhost), no subdomain
    if host in ['localhost', '127.0.0.1']:
        return None
    
    # For production (company.greenpm.com), extract company
    if len(parts) >= 3 and parts[-2:] == ['greenpm', 'com']:
        return parts[0]
    
    # For custom domains, might need different logic
    return None

class MultiTenantMiddleware:
    """Middleware to handle multi-tenant context"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract host and subdomain
        headers = dict(scope.get("headers", []))
        host = headers.get(b"host", b"").decode()
        subdomain = extract_subdomain_from_host(host)
        
        # Set tenant context
        company_id = None
        if subdomain:
            company = await resolve_tenant_from_subdomain(subdomain)
            if company:
                company_id = company.id
        
        # Set context for this request
        with TenantContext(company_id=company_id):
            await self.app(scope, receive, send)

def require_company_access(company_id: int) -> None:
    """Require access to a specific company"""
    current_company = get_current_company_id()
    current_role = get_current_user_role()
    
    # Platform admins can access any company
    if is_current_user_platform_admin():
        return
    
    # Users can only access their own company
    if current_company != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

def require_platform_admin() -> None:
    """Require platform admin access"""
    if not is_current_user_platform_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required"
        )

def get_tenant_filter() -> Dict[str, Any]:
    """Get filter for tenant isolation in queries"""
    company_id = get_current_company_id()
    
    # Platform admins see all data (no filter)
    if is_current_user_platform_admin():
        return {}
    
    # Regular users see only their company's data
    if company_id:
        return {"company_id": company_id}
    
    # No company context - return empty filter (will show no data)
    return {"company_id": -1}  # Non-existent company ID

async def ensure_tenant_isolation(db: AsyncSession) -> None:
    """Ensure row-level security for tenant isolation"""
    company_id = get_current_company_id()
    
    # Skip for platform admins
    if is_current_user_platform_admin():
        return
    
    # Set session variable for RLS
    if company_id:
        await db.execute(
            text("SET LOCAL app.current_company_id = :company_id"),
            {"company_id": company_id}
        )
    else:
        # No company context - set to invalid ID
        await db.execute(
            text("SET LOCAL app.current_company_id = -1")
        )