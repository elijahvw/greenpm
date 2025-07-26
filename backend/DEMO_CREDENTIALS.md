# Demo Credentials - Green PM

## ✅ Working Login Credentials

All demo accounts use the password: **`password123`**

### 🔧 Platform Admin
- **Email**: `admin@greenpm.com`
- **Password**: `password123`
- **Role**: Platform Admin
- **Access**: Full system access, can manage all companies
- **Company**: None (platform-level access)

### 🏢 Landlord Accounts
- **Email**: `landlord@demo.com`
- **Password**: `password123`
- **Role**: Landlord
- **Access**: Company-level property management
- **Company**: Default Company

- **Email**: `landlord@example.com`
- **Password**: `password123`
- **Role**: Landlord
- **Access**: Company-level property management
- **Company**: Default Company

### 🏠 Tenant Account
- **Email**: `tenant@demo.com`
- **Password**: `password123`
- **Role**: Tenant
- **Access**: Tenant portal features
- **Company**: Default Company

## 🔐 Authentication Status

✅ **All credentials are working**
✅ **Password hashes regenerated with compatible bcrypt version**
✅ **API endpoints returning proper user data**
✅ **Token generation and validation working**
✅ **Multi-tenant structure in place**

## 🏗️ Multi-Tenant Setup

### Company Structure
- **Default Company** (subdomain: `default`)
  - Plan: Starter ($29/month)
  - Features: 8/15 enabled
  - Users: 5 (1 landlord, 4 tenants)
  - Data: 3 properties, 3 leases

### Platform Admin
- **admin@greenpm.com** - Platform-level access
- Can access all companies
- No company assignment (platform-wide access)

## 🧪 Testing

### API Endpoints
- `POST /api/v1/auth/login` - ✅ Working
- `GET /api/v1/auth/me` - ✅ Working
- Token-based authentication - ✅ Working

### Frontend Login
Use these credentials on the login page:
1. **Admin**: admin@greenpm.com / password123
2. **Landlord**: landlord@demo.com / password123
3. **Tenant**: tenant@demo.com / password123

## 🔧 Technical Notes

### Fixed Issues
1. **bcrypt compatibility** - Downgraded to version 3.2.2
2. **Password hashes** - Regenerated with working bcrypt
3. **UserResponse schema** - Added missing required fields
4. **SQL queries** - Updated to include all user fields
5. **Multi-tenant migration** - Completed successfully

### Database Status
- All users have valid password hashes
- Company assignments are correct
- Feature flags are configured
- Plan assignments are active

---

**Ready for testing!** 🚀