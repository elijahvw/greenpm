# Green PM - Setup Guide

This guide will walk you through setting up and deploying the Green PM rental property management platform on Google Cloud Platform.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) (>= 1.0)
- [Node.js](https://nodejs.org/) (>= 18.x)
- [Python](https://www.python.org/) (>= 3.11)
- [Docker](https://docs.docker.com/get-docker/)

## Initial Setup

### 1. Google Cloud Project Setup

1. Create a new Google Cloud project or use existing one:
   ```bash
   gcloud projects create greenpm --name="Green PM"
   ```

2. Set the project as default:
   ```bash
   gcloud config set project greenpm
   ```

3. Enable billing for the project (required for Cloud Run, Cloud SQL, etc.)

4. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

### 2. Clone and Setup Repository

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd greenpm
   ```

2. Make deployment script executable:
   ```bash
   chmod +x scripts/deploy.sh
   ```

### 3. Initial Platform Setup

Run the setup command to enable APIs and create required resources:

```bash
./scripts/deploy.sh setup
```

This will:
- Enable all required Google Cloud APIs
- Create Terraform state buckets for dev and prod environments
- Set up basic project configuration

## Configuration

### 1. External Service API Keys

You'll need to obtain API keys for the following services:

#### Stripe (Payment Processing)
1. Create a [Stripe account](https://stripe.com)
2. Get your API keys from the Stripe Dashboard
3. For development, use test keys

#### Twilio (SMS Notifications)
1. Create a [Twilio account](https://twilio.com)
2. Get your Account SID, Auth Token, and phone number
3. Verify your phone number for development

#### SendGrid (Email Notifications)
1. Create a [SendGrid account](https://sendgrid.com)
2. Generate an API key with mail send permissions

#### Firebase (Authentication - Optional)
1. Create a [Firebase project](https://console.firebase.google.com)
2. Enable Authentication with Email/Password and Google providers
3. Download the service account key JSON

### 2. Update Secrets

After deployment, update the placeholder secrets with actual values:

```bash
# Stripe
echo "sk_test_your_stripe_secret_key" | gcloud secrets versions add greenpm-dev-stripe-secret-key --data-file=-
echo "pk_test_your_stripe_publishable_key" | gcloud secrets versions add greenpm-dev-stripe-publishable-key --data-file=-

# Twilio
echo "your_twilio_account_sid" | gcloud secrets versions add greenpm-dev-twilio-account-sid --data-file=-
echo "your_twilio_auth_token" | gcloud secrets versions add greenpm-dev-twilio-auth-token --data-file=-
echo "+1234567890" | gcloud secrets versions add greenpm-dev-twilio-phone-number --data-file=-

# SendGrid
echo "SG.your_sendgrid_api_key" | gcloud secrets versions add greenpm-dev-sendgrid-api-key --data-file=-

# Firebase (paste the entire JSON config)
cat firebase-config.json | gcloud secrets versions add greenpm-dev-firebase-config --data-file=-
```

## Deployment

### Development Environment

Deploy the development environment:

```bash
./scripts/deploy.sh deploy dev
```

This will:
1. Deploy infrastructure (VPC, Cloud SQL, Cloud Run, etc.)
2. Set up placeholder secrets
3. Build and deploy backend and frontend applications

### Production Environment

Deploy the production environment:

```bash
./scripts/deploy.sh deploy prod
```

**Note:** For production, make sure to:
1. Use production API keys for all external services
2. Configure a custom domain name in the Terraform variables
3. Review and adjust resource sizing in `infrastructure/terraform/environments/prod/main.tf`

## Post-Deployment Configuration

### 1. Database Setup

The database will be automatically created, but you may want to:

1. Connect to the database to verify setup:
   ```bash
   gcloud sql connect greenpm-dev-db --user=greenpm_user
   ```

2. Run any additional database setup scripts if needed

### 2. Domain Configuration (Production)

If you have a custom domain:

1. Update the domain name in `infrastructure/terraform/environments/prod/main.tf`
2. Redeploy infrastructure:
   ```bash
   ./scripts/deploy.sh infra prod
   ```
3. Point your domain's DNS to the load balancer IP address

### 3. SSL Certificate

For production with a custom domain:
- The managed SSL certificate will be automatically provisioned
- It may take 10-60 minutes to become active
- Verify certificate status in the Google Cloud Console

## Accessing the Application

After deployment, you'll get URLs for both environments:

- **Development:**
  - Frontend: `https://greenpm-dev-frontend-[region]-[project].a.run.app`
  - Backend API: `https://greenpm-dev-backend-[region]-[project].a.run.app`

- **Production:**
  - Frontend: `https://greenpm-prod-frontend-[region]-[project].a.run.app`
  - Backend API: `https://greenpm-prod-backend-[region]-[project].a.run.app`

## Default Admin User

Create an admin user through the API or database:

```bash
# Using the API (replace with your backend URL)
curl -X POST "https://your-backend-url/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@greenpm.com",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'
```

Then update the user role to admin in the database or through the admin panel.

## Monitoring and Logs

### Application Logs
```bash
# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=greenpm-dev-backend" --limit=50

# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=greenpm-dev-frontend" --limit=50
```

### Database Logs
```bash
gcloud logs read "resource.type=cloudsql_database" --limit=50
```

### Infrastructure Monitoring
- Use Google Cloud Console to monitor Cloud Run services
- Set up alerting policies for critical metrics
- Monitor Cloud SQL performance and connections

## Troubleshooting

### Common Issues

1. **Cloud Run deployment fails:**
   - Check that all required APIs are enabled
   - Verify service account permissions
   - Check Cloud Build logs for build errors

2. **Database connection issues:**
   - Ensure VPC connector is properly configured
   - Verify Cloud SQL instance is running
   - Check database credentials in Secret Manager

3. **External API integration issues:**
   - Verify API keys are correctly stored in Secret Manager
   - Check API key permissions and quotas
   - Review application logs for specific error messages

### Getting Help

1. Check application logs using the commands above
2. Review Google Cloud Console for service status
3. Verify all secrets are properly configured
4. Check Terraform state for infrastructure issues

## Maintenance

### Regular Updates

1. **Update dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt --upgrade
   
   # Frontend
   cd frontend && npm update
   ```

2. **Redeploy applications:**
   ```bash
   ./scripts/deploy.sh apps dev
   ./scripts/deploy.sh apps prod
   ```

### Backup Strategy

- Database backups are automatically configured
- Application code is stored in version control
- Secrets are managed through Google Secret Manager
- Infrastructure is defined as code with Terraform

### Scaling

- Cloud Run automatically scales based on traffic
- Database can be scaled vertically through Terraform configuration
- Storage buckets scale automatically

## Security Considerations

1. **Secrets Management:**
   - Never commit API keys to version control
   - Use Google Secret Manager for all sensitive data
   - Rotate API keys regularly

2. **Network Security:**
   - Database is only accessible through VPC
   - Cloud Run services use HTTPS only
   - Firewall rules restrict access appropriately

3. **Authentication:**
   - Implement strong password policies
   - Enable two-factor authentication for admin users
   - Use Firebase Auth for additional security features

4. **Monitoring:**
   - Set up alerting for unusual activity
   - Monitor failed login attempts
   - Review audit logs regularly

## Cost Optimization

1. **Development Environment:**
   - Use smaller instance sizes
   - Set minimum instances to 0
   - Use smaller database tiers

2. **Production Environment:**
   - Monitor usage and adjust resources accordingly
   - Use committed use discounts for predictable workloads
   - Implement proper caching strategies

3. **Storage:**
   - Set up lifecycle policies for old files
   - Use appropriate storage classes
   - Monitor storage usage regularly