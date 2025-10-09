import os
from fastapi import UploadFile
from typing import Optional
import logging
from .supabase_client import get_supabase

logger = logging.getLogger(__name__)

async def save_file_to_storage(file: UploadFile, uuid: str) -> str:
    """
    Save a file to Supabase Storage and return its public URL
    """
    try:
        # Read file content
        content = await file.read()
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid}{file_ext}"
        
        # Upload to Supabase storage
        supabase = get_supabase()
        bucket_name = "physical-hyperlinks"
        
        # Ensure bucket exists
        try:
            supabase.storage.get_bucket(bucket_name)
        except:
            supabase.storage.create_bucket(bucket_name)
        
        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            file_name,
            content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        logger.info(f"File uploaded successfully: {public_url}")
        
        return public_url
    
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise

def save_file_locally(file: UploadFile, path: str) -> str:
    """For local development only"""
    if os.getenv("VERCEL_ENV"):
        raise Exception("Cannot save files locally in production")
        
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
        file.file.seek(0)
    return path