"""
Green PM - Admin Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SystemHealth(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

class UserManagement(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    properties_count: Optional[int] = 0
    leases_count: Optional[int] = 0
    payments_count: Optional[int] = 0

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_properties: int
    total_leases: int
    active_leases: int
    total_payments: int
    total_revenue: float
    pending_maintenance: int
    system_health: SystemHealth
    server_uptime: str
    database_status: str
    
    # Recent activity
    recent_registrations: int
    recent_payments: int
    recent_maintenance: int

class UserStats(BaseModel):
    total_users: int
    active_users: int
    landlords: int
    tenants: int
    property_managers: int
    pending_users: int
    suspended_users: int
    new_users_this_month: int
    user_growth_rate: float

class PropertyStats(BaseModel):
    total_properties: int
    occupied_properties: int
    vacant_properties: int
    maintenance_pending: int
    average_rent: float
    total_square_footage: Optional[float] = None
    properties_by_type: Dict[str, int] = {}
    properties_by_location: Dict[str, int] = {}

class FinancialStats(BaseModel):
    total_revenue: float
    monthly_revenue: float
    outstanding_rent: float
    security_deposits: float
    maintenance_costs: float
    average_rent_per_unit: float
    collection_rate: float
    revenue_trend: List[Dict[str, Any]] = []

class ActivityLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    # User info
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class AnalyticsReport(BaseModel):
    report_type: str
    date_range: Dict[str, datetime]
    data: Dict[str, Any]
    metrics: Dict[str, float]
    charts: List[Dict[str, Any]] = []
    generated_at: datetime

class MaintenanceStats(BaseModel):
    total_requests: int
    pending_requests: int
    in_progress_requests: int
    completed_requests: int
    overdue_requests: int
    average_completion_time: float
    total_maintenance_cost: float
    requests_by_priority: Dict[str, int] = {}
    requests_by_category: Dict[str, int] = {}

class TenantSatisfaction(BaseModel):
    average_rating: float
    total_reviews: int
    satisfaction_trend: List[Dict[str, Any]] = []
    common_complaints: List[Dict[str, Any]] = []
    response_time_rating: float

class SystemSettings(BaseModel):
    maintenance_enabled: bool = True
    email_notifications: bool = True
    sms_notifications: bool = True
    automatic_backups: bool = True
    backup_frequency: str = "daily"
    max_file_upload_size: int = 10485760  # 10MB
    session_timeout: int = 3600  # 1 hour
    password_complexity: Dict[str, Any] = {}

class BackupStatus(BaseModel):
    last_backup: Optional[datetime] = None
    backup_size: Optional[int] = None
    backup_location: Optional[str] = None
    backup_status: str = "unknown"
    next_scheduled_backup: Optional[datetime] = None

class SecurityAudit(BaseModel):
    failed_login_attempts: int
    suspicious_activities: int
    blocked_ips: List[str] = []
    security_alerts: List[Dict[str, Any]] = []
    last_security_scan: Optional[datetime] = None

class PerformanceMetrics(BaseModel):
    api_response_time: float
    database_response_time: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int
    error_rate: float