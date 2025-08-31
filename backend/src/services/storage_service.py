"""
Storage service for handling file uploads and management
"""
import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Service for handling file storage operations"""
    
    def __init__(self):
        # Support multiple buckets
        self.documents_bucket = os.getenv("DOCUMENTS_BUCKET", "greenpm-documents")
        self.property_images_bucket = os.getenv("PROPERTY_IMAGES_BUCKET", "greenpm-property-images") 
        self.default_bucket = os.getenv("GCS_BUCKET_NAME", "greenpm-storage")
        
        try:
            self.client = storage.Client()
        except Exception as e:
            logger.warning(f"Could not initialize GCS client: {e}")
            self.client = None
    
    async def upload_document(
        self, 
        file: UploadFile, 
        path: str, 
        user_id: str,
        bucket_type: str = "documents"
    ) -> str:
        """
        Upload a document to cloud storage
        
        Args:
            file: The uploaded file
            path: Storage path for the file
            user_id: ID of the user uploading the file
            bucket_type: Type of bucket ("documents", "property_images", or "default")
            
        Returns:
            URL of the uploaded file
        """
        try:
            # Select appropriate bucket
            if bucket_type == "documents":
                bucket_name = self.documents_bucket
            elif bucket_type == "property_images":
                bucket_name = self.property_images_bucket
            else:
                bucket_name = self.default_bucket
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            full_path = f"{path}/{unique_filename}"
            
            # If GCS is not available, simulate upload (for development)
            if not self.client:
                logger.warning("GCS not available, simulating file upload")
                return f"https://storage.googleapis.com/{bucket_name}/{full_path}"
            
            # Get the bucket
            bucket = self.client.bucket(bucket_name)
            
            # Upload to GCS
            blob = bucket.blob(full_path)
            
            # Read file content
            content = await file.read()
            
            # Upload with metadata
            blob.upload_from_string(
                content,
                content_type=file.content_type or 'application/octet-stream'
            )
            
            # Make blob publicly readable (adjust based on your security requirements)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
    
    async def delete_document(self, file_url: str) -> bool:
        """
        Delete a document from cloud storage
        
        Args:
            file_url: URL of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.client:
                logger.warning("GCS not available, simulating file deletion")
                return True
            
            # Extract bucket name and blob name from URL
            # URL format: https://storage.googleapis.com/bucket_name/path/to/file
            url_parts = file_url.split('/')
            if len(url_parts) < 5:
                logger.error(f"Invalid file URL format: {file_url}")
                return False
                
            bucket_name = url_parts[3]  # bucket name is the 4th part
            blob_name = '/'.join(url_parts[4:])  # everything after bucket name
            
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            if blob.exists():
                blob.delete()
                return True
            else:
                logger.warning(f"File not found: {blob_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_signed_url(self, blob_name: str, bucket_name: str = None, expiration_minutes: int = 60) -> Optional[str]:
        """
        Generate a signed URL for private file access
        
        Args:
            blob_name: Name of the blob in storage
            bucket_name: Name of the bucket (defaults to documents bucket)
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL or None if failed
        """
        try:
            if not self.client:
                logger.warning("GCS not available, cannot generate signed URL")
                return None
            
            # Use documents bucket as default
            bucket_name = bucket_name or self.documents_bucket
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Generate signed URL
            from datetime import datetime, timedelta
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            
            return signed_url
            
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            return None