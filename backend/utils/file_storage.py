"""
File Storage Utility
Handles file uploads to local filesystem or cloud storage (Supabase, S3, etc.)
"""
import os
import uuid
from pathlib import Path
from typing import Optional, BinaryIO, Union
from fastapi import UploadFile
import aiofiles  # type: ignore[import-not-found]

from backend.config import settings


class FileStorage:
    """
    Unified file storage handler supporting:
    - Local filesystem (development)
    - Supabase Storage (production - recommended)
    - AWS S3 (production - alternative)
    """
    
    def __init__(self):
        self.storage_type = os.getenv("FILE_STORAGE_TYPE", "local")  # local, supabase, s3
        self.local_upload_dir = Path("uploads")
        
        # Initialize Supabase client if configured
        self.supabase_client = None
        self.supabase_bucket = os.getenv("SUPABASE_BUCKET_NAME", "resumes")
        
        if self.storage_type == "supabase":
            try:
                from supabase import create_client  # type: ignore[import-untyped]
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                
                if supabase_url and supabase_key:
                    self.supabase_client = create_client(supabase_url, supabase_key)
                    print(f"✅ Supabase Storage initialized (bucket: {self.supabase_bucket})")
                else:
                    print("⚠️ WARNING: SUPABASE_URL or SUPABASE_KEY not set, falling back to local storage")
                    self.storage_type = "local"
            except ImportError:
                print("⚠️ WARNING: supabase-py not installed, falling back to local storage")
                self.storage_type = "local"
        
        # Initialize AWS S3 if configured
        self.s3_client = None
        self.s3_bucket = os.getenv("AWS_S3_BUCKET_NAME")
        
        if self.storage_type == "s3":
            try:
                import boto3  # type: ignore[import-not-found]
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                print(f"✅ AWS S3 Storage initialized (bucket: {self.s3_bucket})")
            except ImportError:
                print("⚠️ WARNING: boto3 not installed, falling back to local storage")
                self.storage_type = "local"
    
    async def save_upload(
        self,
        file: UploadFile,
        subfolder: str = "",
        user_id: Optional[str] = None,
        custom_filename: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Save uploaded file to storage.
        
        Args:
            file: FastAPI UploadFile object
            subfolder: Subfolder to organize files (e.g., 'resumes', 'cover_letters')
            user_id: Optional user identifier for file organization
            custom_filename: Optional custom name (otherwise uses original filename)
        
        Returns:
            Tuple of (file_path, public_url)
            - file_path: Path/key used to reference the file
            - public_url: Public URL to access the file (if applicable)
        """
        # Generate unique filename
        file_ext = Path(file.filename).suffix if file.filename else ""
        unique_id = str(uuid.uuid4())[:8]
        
        if custom_filename:
            filename = f"{unique_id}_{custom_filename}"
        elif user_id:
            base_name = Path(file.filename).stem if file.filename else "file"
            filename = f"{user_id}_{unique_id}_{base_name}{file_ext}"
        else:
            filename = f"{unique_id}_{file.filename}" if file.filename else f"{unique_id}{file_ext}"
        
        # Read file content
        content = await file.read()
        
        # Save based on storage type
        if self.storage_type == "supabase" and self.supabase_client:
            return await self._save_to_supabase(content, filename, subfolder)
        elif self.storage_type == "s3" and self.s3_client:
            return await self._save_to_s3(content, filename, subfolder)
        else:
            return await self._save_to_local(content, filename, subfolder)
    
    async def _save_to_local(self, content: bytes, filename: str, subfolder: str) -> tuple[str, str]:
        """Save file to local filesystem"""
        upload_path = self.local_upload_dir / subfolder if subfolder else self.local_upload_dir
        upload_path.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_path / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Return relative path and a local URL (for compatibility)
        rel_path = str(file_path.relative_to(Path.cwd()))
        local_url = f"/files/{rel_path}"  # This would need a static file route
        
        print(f"📁 File saved locally: {rel_path}")
        return rel_path, local_url
    
    async def _save_to_supabase(self, content: bytes, filename: str, subfolder: str) -> tuple[str, str]:
        """Save file to Supabase Storage"""
        try:
            # Construct storage path
            storage_path = f"{subfolder}/{filename}" if subfolder else filename
            
            # Upload to Supabase
            response = self.supabase_client.storage.from_(self.supabase_bucket).upload(  # type: ignore[union-attr]
                path=storage_path,
                file=content,
                file_options={"content-type": "application/pdf"}  # Adjust based on file type
            )
            
            # Get public URL
            public_url = self.supabase_client.storage.from_(self.supabase_bucket).get_public_url(storage_path)  # type: ignore[union-attr]
            
            print(f"☁️ File saved to Supabase: {storage_path}")
            return storage_path, public_url
        
        except Exception as e:
            print(f"❌ Supabase upload failed: {e}, falling back to local storage")
            return await self._save_to_local(content, filename, subfolder)
    
    async def _save_to_s3(self, content: bytes, filename: str, subfolder: str) -> tuple[str, str]:
        """Save file to AWS S3"""
        try:
            # Construct S3 key
            s3_key = f"{subfolder}/{filename}" if subfolder else filename
            
            # Upload to S3
            self.s3_client.put_object(  # type: ignore[union-attr]
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=content,
                ContentType="application/pdf"  # Adjust based on file type
            )
            
            # Get public URL (assuming public bucket or presigned URL)
            public_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            
            print(f"☁️ File saved to S3: {s3_key}")
            return s3_key, public_url
        
        except Exception as e:
            print(f"❌ S3 upload failed: {e}, falling back to local storage")
            return await self._save_to_local(content, filename, subfolder)
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content from storage.
        
        Args:
            file_path: Path/key returned from save_upload
        
        Returns:
            File content as bytes, or None if not found
        """
        if self.storage_type == "supabase" and self.supabase_client:
            return await self._get_from_supabase(file_path)
        elif self.storage_type == "s3" and self.s3_client:
            return await self._get_from_s3(file_path)
        else:
            return await self._get_from_local(file_path)
    
    async def _get_from_local(self, file_path: str) -> Optional[bytes]:
        """Get file from local filesystem"""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
    
    async def _get_from_supabase(self, file_path: str) -> Optional[bytes]:
        """Get file from Supabase Storage"""
        try:
            response = self.supabase_client.storage.from_(self.supabase_bucket).download(file_path)  # type: ignore[union-attr]
            return response
        except Exception as e:
            print(f"❌ Failed to retrieve from Supabase: {e}")
            return None
    
    async def _get_from_s3(self, file_path: str) -> Optional[bytes]:
        """Get file from AWS S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=file_path)  # type: ignore[union-attr]
            return response['Body'].read()
        except Exception as e:
            print(f"❌ Failed to retrieve from S3: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_path: Path/key of the file to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        if self.storage_type == "supabase" and self.supabase_client:
            return await self._delete_from_supabase(file_path)
        elif self.storage_type == "s3" and self.s3_client:
            return await self._delete_from_s3(file_path)
        else:
            return await self._delete_from_local(file_path)
    
    async def _delete_from_local(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            Path(file_path).unlink(missing_ok=True)
            print(f"🗑️ Deleted local file: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete local file: {e}")
            return False
    
    async def _delete_from_supabase(self, file_path: str) -> bool:
        """Delete file from Supabase Storage"""
        try:
            self.supabase_client.storage.from_(self.supabase_bucket).remove([file_path])  # type: ignore[union-attr]
            print(f"🗑️ Deleted from Supabase: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete from Supabase: {e}")
            return False
    
    async def _delete_from_s3(self, file_path: str) -> bool:
        """Delete file from AWS S3"""
        try:
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_path)  # type: ignore[union-attr]
            print(f"🗑️ Deleted from S3: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete from S3: {e}")
            return False


# Global file storage instance
file_storage = FileStorage()


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
### Example 1: Save uploaded resume
```python
from fastapi import UploadFile
from backend.utils.file_storage import file_storage

@router.post("/upload-resume")
async def upload_resume(file: UploadFile, user_id: str):
    file_path, public_url = await file_storage.save_upload(
        file=file,
        subfolder="resumes",
        user_id=user_id
    )
    
    # Save file_path to database
    # Use public_url if you need to show it to users
    
    return {"file_path": file_path, "url": public_url}
```

### Example 2: Retrieve file
```python
file_content = await file_storage.get_file("resumes/user123_resume.pdf")
if file_content:
    # Use the file content
    pass
```

### Example 3: Delete file
```python
success = await file_storage.delete_file("resumes/user123_resume.pdf")
```

### Configuration for Production (Render):

Set these environment variables in Render:

**Option 1: Supabase Storage (Recommended)**
```bash
FILE_STORAGE_TYPE=supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET_NAME=resumes
```

**Option 2: AWS S3**
```bash
FILE_STORAGE_TYPE=s3
AWS_S3_BUCKET_NAME=my-linkedin-automation-files
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

**Option 3: Local Storage (Development Only)**
```bash
FILE_STORAGE_TYPE=local
```

⚠️ **WARNING**: Local storage on Render free tier is ephemeral!
Files will be deleted when the service restarts or redeploys.
Use Supabase or S3 for production.
"""
