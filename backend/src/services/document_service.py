"""
Document service for generating lease documents and other legal documents
"""
import os
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.models.lease import Lease
from src.models.property import Property
from src.models.user import User

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for handling document generation operations"""
    
    def __init__(self):
        self.template_path = os.getenv("DOCUMENT_TEMPLATE_PATH", "templates/documents")
        self.output_path = os.getenv("DOCUMENT_OUTPUT_PATH", "generated_documents")
        
        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
    
    async def generate_lease_document(self, lease_id: str, user_id: str) -> Optional[str]:
        """
        Generate a lease document for the given lease
        
        Args:
            lease_id: ID of the lease
            user_id: ID of the user requesting the document
            
        Returns:
            Path to the generated document or None if failed
        """
        try:
            # Get database session
            db = next(get_db())
            
            # Fetch lease with related data
            lease = db.query(Lease).filter(Lease.id == lease_id).first()
            if not lease:
                logger.error(f"Lease not found: {lease_id}")
                return None
            
            # Fetch property and tenant information
            property_obj = db.query(Property).filter(Property.id == lease.property_id).first()
            tenant = db.query(User).filter(User.id == lease.tenant_id).first()
            landlord = db.query(User).filter(User.id == property_obj.owner_id).first()
            
            if not all([property_obj, tenant, landlord]):
                logger.error("Missing required data for lease document generation")
                return None
            
            # Generate document content
            document_content = self._generate_lease_content(lease, property_obj, tenant, landlord)
            
            # Save document
            filename = f"lease_{lease_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = os.path.join(self.output_path, filename)
            
            with open(file_path, 'w') as f:
                f.write(document_content)
            
            logger.info(f"Generated lease document: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating lease document: {e}")
            return None
        finally:
            db.close()
    
    def _generate_lease_content(self, lease: Lease, property_obj: Property, tenant: User, landlord: User) -> str:
        """
        Generate the content for a lease document
        
        Args:
            lease: Lease object
            property_obj: Property object
            tenant: Tenant user object
            landlord: Landlord user object
            
        Returns:
            Generated lease document content
        """
        content = f"""
RESIDENTIAL LEASE AGREEMENT

This Lease Agreement is entered into on {datetime.now().strftime('%B %d, %Y')} between:

LANDLORD:
Name: {landlord.first_name} {landlord.last_name}
Email: {landlord.email}
Phone: {landlord.phone or 'N/A'}

TENANT:
Name: {tenant.first_name} {tenant.last_name}
Email: {tenant.email}
Phone: {tenant.phone or 'N/A'}

PROPERTY DETAILS:
Address: {property_obj.address}
City: {property_obj.city}
State: {property_obj.state}
ZIP Code: {property_obj.zip_code}
Type: {property_obj.property_type}
Bedrooms: {property_obj.bedrooms}
Bathrooms: {property_obj.bathrooms}
Square Feet: {property_obj.square_feet or 'N/A'}

LEASE TERMS:
Start Date: {lease.start_date.strftime('%B %d, %Y')}
End Date: {lease.end_date.strftime('%B %d, %Y')}
Monthly Rent: ${lease.monthly_rent:,.2f}
Security Deposit: ${lease.security_deposit:,.2f}
Status: {lease.status.title()}

TERMS AND CONDITIONS:

1. RENT PAYMENT
   The Tenant agrees to pay rent in the amount of ${lease.monthly_rent:,.2f} per month, 
   due on the 1st day of each month.

2. SECURITY DEPOSIT
   A security deposit of ${lease.security_deposit:,.2f} is required and will be held 
   by the Landlord as security for the performance of the Tenant's obligations.

3. USE OF PREMISES
   The premises shall be used solely as a private residential dwelling.

4. MAINTENANCE AND REPAIRS
   The Tenant agrees to maintain the premises in good condition and promptly report 
   any needed repairs to the Landlord.

5. TERMINATION
   This lease may be terminated by either party with proper notice as required by law.

By signing below, both parties agree to the terms and conditions of this lease agreement.

LANDLORD SIGNATURE: ___________________________ DATE: ___________

TENANT SIGNATURE: _____________________________ DATE: ___________

Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Lease ID: {lease.id}
"""
        return content
    
    async def generate_lease_termination_document(self, lease_id: str, termination_date: datetime, reason: str) -> Optional[str]:
        """
        Generate a lease termination document
        
        Args:
            lease_id: ID of the lease being terminated
            termination_date: Date of termination
            reason: Reason for termination
            
        Returns:
            Path to the generated document or None if failed
        """
        try:
            # Get database session
            db = next(get_db())
            
            # Fetch lease with related data
            lease = db.query(Lease).filter(Lease.id == lease_id).first()
            if not lease:
                logger.error(f"Lease not found: {lease_id}")
                return None
            
            # Fetch property and tenant information
            property_obj = db.query(Property).filter(Property.id == lease.property_id).first()
            tenant = db.query(User).filter(User.id == lease.tenant_id).first()
            landlord = db.query(User).filter(User.id == property_obj.owner_id).first()
            
            if not all([property_obj, tenant, landlord]):
                logger.error("Missing required data for termination document generation")
                return None
            
            # Generate termination document content
            content = f"""
LEASE TERMINATION NOTICE

Date: {datetime.now().strftime('%B %d, %Y')}

TO: {tenant.first_name} {tenant.last_name}
TENANT(S) IN POSSESSION OF: {property_obj.address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}

FROM: {landlord.first_name} {landlord.last_name}
LANDLORD

NOTICE OF TERMINATION OF TENANCY

YOU ARE HEREBY NOTIFIED that your tenancy of the above-described premises is hereby terminated effective {termination_date.strftime('%B %d, %Y')}.

REASON FOR TERMINATION: {reason}

ORIGINAL LEASE DETAILS:
- Lease Start Date: {lease.start_date.strftime('%B %d, %Y')}
- Lease End Date: {lease.end_date.strftime('%B %d, %Y')}
- Monthly Rent: ${lease.monthly_rent:,.2f}
- Security Deposit: ${lease.security_deposit:,.2f}

You are required to quit and surrender the premises to the Landlord on or before the termination date specified above.

If you fail to do so, legal proceedings will be instituted against you to recover possession of said premises, damages, and costs of suit.

DATED: {datetime.now().strftime('%B %d, %Y')}

LANDLORD: {landlord.first_name} {landlord.last_name}

Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Lease ID: {lease.id}
"""
            
            # Save document
            filename = f"termination_{lease_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file_path = os.path.join(self.output_path, filename)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Generated termination document: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating termination document: {e}")
            return None
        finally:
            db.close()