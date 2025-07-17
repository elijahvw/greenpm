# Green PM - Architecture Documentation

## Overview

Green PM is a comprehensive rental property management platform built on Google Cloud Platform (GCP) using modern cloud-native technologies. The platform follows a microservices architecture with clear separation of concerns and scalable design patterns.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Cloud CDN     │    │   Cloud Armor   │
│   (HTTPS/SSL)   │────│   (Static       │────│   (Security)    │
│                 │    │   Assets)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React)                           │
│                   Cloud Run Service                            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼ API Calls
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                           │
│                   Cloud Run Service                            │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud SQL     │    │  Cloud Storage  │    │ Secret Manager  │
│  (PostgreSQL)   │    │   (Files/Docs)  │    │  (API Keys)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Redux Toolkit + React Query
- **Authentication:** Firebase Auth (optional) + JWT
- **Payment Processing:** Stripe Elements
- **Build Tool:** Create React App
- **Deployment:** Cloud Run (containerized with Nginx)

### Backend
- **Framework:** FastAPI (Python)
- **Database ORM:** SQLAlchemy with Alembic migrations
- **Authentication:** JWT + Firebase Auth integration
- **API Documentation:** OpenAPI/Swagger (auto-generated)
- **Background Tasks:** Celery with Redis (future enhancement)
- **Deployment:** Cloud Run (containerized)

### Infrastructure
- **Cloud Provider:** Google Cloud Platform
- **Container Registry:** Google Container Registry
- **Database:** Cloud SQL (PostgreSQL)
- **File Storage:** Cloud Storage
- **Secrets:** Google Secret Manager
- **Networking:** VPC with private subnets
- **Load Balancing:** Google Cloud Load Balancer
- **SSL/TLS:** Google-managed SSL certificates
- **CI/CD:** Cloud Build
- **Infrastructure as Code:** Terraform

### External Services
- **Payment Processing:** Stripe
- **SMS Notifications:** Twilio
- **Email Notifications:** SendGrid
- **Authentication:** Firebase Auth (optional)

## Detailed Component Architecture

### 1. Frontend Architecture

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components (buttons, forms, etc.)
│   ├── auth/           # Authentication components
│   ├── property/       # Property-related components
│   ├── lease/          # Lease management components
│   ├── payment/        # Payment components
│   └── maintenance/    # Maintenance request components
├── pages/              # Page components
│   ├── public/         # Public pages (home, property listings)
│   ├── auth/           # Authentication pages
│   ├── dashboard/      # Dashboard pages
│   └── admin/          # Admin pages
├── hooks/              # Custom React hooks
├── services/           # API service functions
├── store/              # Redux store configuration
├── contexts/           # React contexts
├── utils/              # Utility functions
└── types/              # TypeScript type definitions
```

#### Key Frontend Features:
- **Responsive Design:** Mobile-first approach with Tailwind CSS
- **Real-time Updates:** WebSocket integration for live notifications
- **Offline Support:** Service worker for basic offline functionality
- **Progressive Web App:** PWA capabilities for mobile installation
- **Accessibility:** WCAG 2.1 AA compliance
- **Performance:** Code splitting and lazy loading

### 2. Backend Architecture

```
src/
├── api/                # API endpoints
│   └── v1/
│       ├── endpoints/  # Route handlers
│       └── router.py   # Main API router
├── core/               # Core functionality
│   ├── config.py       # Configuration settings
│   ├── database.py     # Database connection
│   ├── security.py     # Security utilities
│   └── logging.py      # Logging configuration
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── services/           # Business logic services
├── dependencies/       # FastAPI dependencies
├── middleware/         # Custom middleware
├── utils/              # Utility functions
└── tests/              # Test files
```

#### Key Backend Features:
- **RESTful API:** OpenAPI 3.0 compliant with auto-generated documentation
- **Authentication:** JWT-based with role-based access control (RBAC)
- **Data Validation:** Pydantic models for request/response validation
- **Database Migrations:** Alembic for schema versioning
- **Background Tasks:** Async task processing
- **Monitoring:** Structured logging with Cloud Logging integration
- **Security:** Input validation, rate limiting, CORS protection

### 3. Database Schema

#### Core Entities:
- **Users:** Landlords, tenants, and admin users
- **Properties:** Rental properties with details and images
- **Leases:** Rental agreements and terms
- **Payments:** Rent payments and financial transactions
- **Maintenance Requests:** Property maintenance and repairs
- **Messages:** In-app communication system
- **Applications:** Rental applications and screening
- **Audit Logs:** System activity tracking

#### Key Relationships:
```sql
Users (1:N) Properties (1:N) Leases (1:N) Payments
Users (1:N) MaintenanceRequests
Users (1:N) Messages
Properties (1:N) Applications
Leases (1:N) LeaseDocuments
```

### 4. Security Architecture

#### Authentication Flow:
1. User registers/logs in through frontend
2. Backend validates credentials
3. JWT token issued with user claims
4. Token included in subsequent API requests
5. Middleware validates token and extracts user context

#### Authorization:
- **Role-Based Access Control (RBAC)**
- **Resource-Level Permissions**
- **API Rate Limiting**
- **Input Validation and Sanitization**

#### Data Protection:
- **Encryption at Rest:** Cloud SQL encryption
- **Encryption in Transit:** HTTPS/TLS 1.3
- **Secrets Management:** Google Secret Manager
- **PII Protection:** Data anonymization and encryption

## Deployment Architecture

### Development Environment
```
┌─────────────────┐
│   Developer     │
│   Machine       │
└─────────────────┘
          │
          ▼ git push
┌─────────────────┐
│   GitHub        │
│   Repository    │
└─────────────────┘
          │
          ▼ webhook
┌─────────────────┐
│   Cloud Build   │
│   (CI/CD)       │
└─────────────────┘
          │
          ▼ deploy
┌─────────────────┐
│   Cloud Run     │
│   (Dev)         │
└─────────────────┘
```

### Production Environment
```
┌─────────────────┐
│   GitHub        │
│   (main branch) │
└─────────────────┘
          │
          ▼ webhook
┌─────────────────┐
│   Cloud Build   │
│   (Production)  │
└─────────────────┘
          │
          ▼ deploy
┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │────│  Load Balancer  │
│   (Production)  │    │   (Global)      │
└─────────────────┘    └─────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- **Cloud Run:** Auto-scales based on request volume
- **Database:** Read replicas for read-heavy workloads
- **Storage:** Cloud Storage scales automatically
- **CDN:** Global content distribution

### Performance Optimization
- **Caching:** Redis for session and application caching
- **Database Indexing:** Optimized queries with proper indexes
- **Image Optimization:** Automatic image resizing and compression
- **API Response Caching:** HTTP caching headers

### Monitoring and Observability
- **Application Monitoring:** Cloud Monitoring and Alerting
- **Log Aggregation:** Cloud Logging with structured logs
- **Error Tracking:** Integrated error reporting
- **Performance Metrics:** Custom metrics and dashboards

## Data Flow

### User Registration Flow
1. User submits registration form
2. Frontend validates input
3. API creates user record
4. Email verification sent
5. User confirms email
6. Account activated

### Property Listing Flow
1. Landlord creates property listing
2. Images uploaded to Cloud Storage
3. Property data stored in database
4. Listing published to public site
5. Search indexes updated

### Lease Signing Flow
1. Landlord creates lease document
2. Tenant reviews and signs digitally
3. Document stored in Cloud Storage
4. Lease status updated
5. Notifications sent to both parties

### Payment Processing Flow
1. Tenant initiates payment
2. Stripe processes payment
3. Webhook confirms payment
4. Database updated
5. Receipt generated and sent

## Security Measures

### Application Security
- **Input Validation:** All inputs validated and sanitized
- **SQL Injection Prevention:** Parameterized queries
- **XSS Protection:** Content Security Policy headers
- **CSRF Protection:** CSRF tokens for state-changing operations

### Infrastructure Security
- **Network Isolation:** VPC with private subnets
- **Firewall Rules:** Restrictive ingress/egress rules
- **Identity and Access Management:** Least privilege principle
- **Secrets Management:** No hardcoded secrets

### Data Security
- **Encryption:** Data encrypted at rest and in transit
- **Backup Security:** Encrypted database backups
- **Access Logging:** All data access logged
- **Data Retention:** Automated data lifecycle management

## Disaster Recovery

### Backup Strategy
- **Database Backups:** Automated daily backups with point-in-time recovery
- **File Backups:** Cloud Storage with versioning enabled
- **Code Repository:** Git-based version control
- **Infrastructure:** Terraform state management

### Recovery Procedures
- **RTO (Recovery Time Objective):** < 4 hours
- **RPO (Recovery Point Objective):** < 1 hour
- **Multi-Region Deployment:** Available for production
- **Automated Failover:** Database and application failover

## Future Enhancements

### Planned Features
- **Mobile Applications:** Native iOS and Android apps
- **Advanced Analytics:** Business intelligence dashboard
- **AI/ML Integration:** Predictive maintenance and pricing
- **Multi-tenancy:** Support for property management companies

### Technical Improvements
- **Microservices:** Split monolithic backend into services
- **Event-Driven Architecture:** Implement event sourcing
- **GraphQL API:** Alternative to REST API
- **Kubernetes:** Migration from Cloud Run to GKE

## Cost Optimization

### Current Optimizations
- **Auto-scaling:** Pay only for resources used
- **Efficient Database Queries:** Minimize database load
- **Image Optimization:** Reduce storage and bandwidth costs
- **Caching:** Reduce API calls and database queries

### Monitoring and Alerts
- **Budget Alerts:** Automated cost monitoring
- **Resource Utilization:** Track and optimize resource usage
- **Performance vs. Cost:** Balance performance and cost efficiency