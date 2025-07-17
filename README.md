# 🏠 Green PM - Rental Property Management Platform

A comprehensive, production-ready SaaS platform for rental property management built on Google Cloud Platform. Green PM provides landlords, tenants, and property managers with all the tools they need to streamline rental operations.

## ✨ Features

### 🏠 **Property Management**
- Property listings with image galleries and virtual tours
- Detailed property information and amenities
- Public property search and filtering
- Property performance analytics

### 📄 **Lease Management**
- Digital lease creation and management
- E-signature integration for lease signing
- Automatic lease renewal notifications
- Lease document storage and versioning

### 💰 **Financial Management**
- Online rent collection via Stripe
- Automated late fee calculations
- Payment history and receipts
- Financial reporting and analytics

### 🔧 **Maintenance & Repairs**
- Tenant maintenance request submission
- Photo upload for maintenance issues
- Work order management system
- Contractor/vendor coordination

### 💬 **Communication**
- In-app messaging system
- SMS notifications via Twilio
- Email notifications via SendGrid
- Message templates and automation

### 📱 **Tenant Portal**
- Online rent payments
- Maintenance request submission
- Lease document access
- Communication with landlords

### 🏢 **Landlord Dashboard**
- Property portfolio overview
- Tenant management
- Financial reporting
- Maintenance tracking

### ⚖️ **Legal & Compliance**
- Automated legal notice generation
- Eviction process tracking
- Document archival system
- Compliance reporting

### 👨‍💼 **Admin Controls**
- Multi-tenant SaaS management
- User and permission management
- Usage analytics and billing
- System monitoring and logs

## 🏗️ Architecture

### **Frontend**
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Redux Toolkit** for state management
- **React Query** for API caching
- **Stripe Elements** for payments

### **Backend**
- **FastAPI** (Python) with async support
- **SQLAlchemy** ORM with PostgreSQL
- **JWT** authentication with role-based access
- **Pydantic** for data validation
- **Alembic** for database migrations

### **Infrastructure**
- **Google Cloud Platform** (GCP)
- **Cloud Run** for containerized applications
- **Cloud SQL** (PostgreSQL) for database
- **Cloud Storage** for file storage
- **Cloud Build** for CI/CD
- **Terraform** for infrastructure as code

### **External Integrations**
- **Stripe** for payment processing
- **Twilio** for SMS notifications
- **SendGrid** for email notifications
- **Firebase Auth** for authentication (optional)

## 🚀 Quick Start

### Prerequisites
- Google Cloud SDK
- Terraform >= 1.0
- Node.js >= 18
- Python >= 3.11
- Docker

### 1. Initial Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd greenpm

# Make deployment script executable
chmod +x scripts/deploy.sh

# Run initial setup
./scripts/deploy.sh setup
```

### 2. Configure API Keys
Update the following secrets in Google Secret Manager:
- Stripe API keys
- Twilio credentials
- SendGrid API key
- Firebase configuration (optional)

### 3. Deploy Development Environment
```bash
./scripts/deploy.sh deploy dev
```

### 4. Deploy Production Environment
```bash
./scripts/deploy.sh deploy prod
```

## 📚 Documentation

- [**Setup Guide**](docs/setup.md) - Complete deployment instructions
- [**Architecture**](docs/architecture.md) - Technical architecture overview
- [**API Documentation**](https://your-backend-url/docs) - Interactive API docs

## 🔧 Development

### Local Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🌐 Deployment

The platform supports both development and production environments:

### Development
- Smaller resource allocations
- Test API keys
- Debug logging enabled
- Auto-scaling from 0 instances

### Production
- Production-grade resources
- Live API keys
- Structured logging
- High availability configuration

## 🔒 Security Features

- **Authentication**: JWT-based with role-based access control
- **Data Encryption**: At rest and in transit
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting and DDoS protection
- **Secrets Management**: Google Secret Manager integration
- **Audit Logging**: Complete audit trail

## 📊 Monitoring & Analytics

- **Application Monitoring**: Cloud Monitoring integration
- **Error Tracking**: Structured error logging
- **Performance Metrics**: Custom dashboards
- **Usage Analytics**: User behavior tracking
- **Cost Monitoring**: Automated cost alerts

## 🔄 CI/CD Pipeline

- **Source Control**: Git-based workflow
- **Build Process**: Cloud Build automation
- **Testing**: Automated test execution
- **Deployment**: Blue-green deployments
- **Rollback**: Automated rollback capabilities

## 💰 Cost Optimization

- **Auto-scaling**: Pay only for resources used
- **Efficient Queries**: Optimized database performance
- **Caching**: Reduced API calls and database load
- **Storage Lifecycle**: Automated file lifecycle management

## 🤝 User Roles

### **Tenant**
- Apply for properties
- Sign leases digitally
- Pay rent online
- Submit maintenance requests
- Message landlords

### **Landlord**
- Manage property listings
- Review applications
- Create and manage leases
- Collect rent payments
- Handle maintenance requests

### **Admin**
- Manage all users and properties
- Access system analytics
- Configure platform settings
- Monitor system health
- Handle billing and subscriptions

## 🛠️ Tech Stack Details

### **Frontend Dependencies**
```json
{
  "react": "^18.2.0",
  "typescript": "^4.9.5",
  "tailwindcss": "^3.3.6",
  "@reduxjs/toolkit": "^1.9.7",
  "react-query": "^3.39.3",
  "@stripe/react-stripe-js": "^2.4.0"
}
```

### **Backend Dependencies**
```python
fastapi==0.104.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
stripe==7.8.0
twilio==8.10.3
sendgrid==6.11.0
```

## 📈 Scalability

The platform is designed to scale horizontally:

- **Application Scaling**: Cloud Run auto-scaling
- **Database Scaling**: Cloud SQL read replicas
- **File Storage**: Unlimited Cloud Storage
- **Global Distribution**: Multi-region deployment ready

## 🔮 Future Roadmap

- [ ] Mobile applications (iOS/Android)
- [ ] Advanced analytics and reporting
- [ ] AI-powered maintenance predictions
- [ ] Multi-language support
- [ ] Advanced workflow automation
- [ ] Integration marketplace

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Check the [documentation](docs/)
- Review [architecture guide](docs/architecture.md)
- Follow the [setup guide](docs/setup.md)

## 🏆 Key Benefits

### **For Landlords**
- ⏰ Save time with automated processes
- 💰 Faster rent collection
- 📊 Better financial insights
- 🔧 Streamlined maintenance management
- 📱 Mobile-friendly interface

### **For Tenants**
- 💳 Convenient online payments
- 📱 Easy maintenance requests
- 💬 Direct landlord communication
- 📄 Digital lease management
- 🔔 Automated notifications

### **For Property Managers**
- 🏢 Multi-property management
- 👥 Team collaboration tools
- 📈 Performance analytics
- ⚖️ Legal compliance features
- 🔒 Enterprise-grade security

---

**Green PM** - Simplifying rental property management with modern technology. 🏠✨
Green Property Management
