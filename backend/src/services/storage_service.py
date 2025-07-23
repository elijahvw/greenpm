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
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "greenpm-storage")
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            logger.warning(f"Could not initialize GCS client: {e}")
            self.client = None
            self.bucket = None
    
    async def upload_document(
        self, 
        file: UploadFile, 
        path: str, 
        user_id: str
    ) -> str:
        """
        Upload a document to cloud storage
        
        Args:
            file: The uploaded file
            path: Storage path for the file
            user_id: ID of the user uploading the file
            
        Returns:
            URL of the uploaded file
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            full_path = f"{path}/{unique_filename}"
            
            # If GCS is not available, simulate upload (for development)
            if not self.client or not self.bucket:
                logger.warning("GCS not available, simulating file upload")
                return f"https://storage.googleapis.com/{self.bucket_name}/{full_path}"
            
            # Upload to GCS
            blob = self.bucket.blob(full_path)
            
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
            if not self.client or not self.bucket:
                logger.warning("GCS not available, simulating file deletion")
                return True
            
            # Extract blob name from URL
            blob_name = file_url.split(f"{self.bucket_name}/")[-1]
            blob = self.bucket.blob(blob_name)
            
            if blob.exists():
                blob.delete()
                return True
            else:
                logger.warning(f"File not found: {blob_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_signed_url(self, blob_name: str, expiration_minutes: int = 60) -> Optional[str]:
        """
        Generate a signed URL for private file access
        
        Args:
            blob_name: Name of the blob in storage
            expiration_minutes: URL expiration time in minutes
            
        Returns:
            Signed URL or None if failed
        """
        try:
            if not self.client or not self.bucket:
                logger.warning("GCS not available, cannot generate signed URL")
                return None
            
            blob = self.bucket.blob(blob_name)
            
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