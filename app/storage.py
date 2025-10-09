import os
from fastapi import UploadFile
from typing import Optional

def save_file_locally(file: UploadFile, path: str) -> str:
    """Temporary function to save files locally during development"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
        file.file.seek(0)  # Reset file pointer
    return path

# TODO: Implement cloud storage integration
# You'll need to implement these functions when setting up cloud storage
# Options include:
# 1. AWS S3
# 2. Cloudinary
# 3. Vercel Blob Storage (beta)
# Example implementation for Vercel Blob Storage will be provided when it's out of beta