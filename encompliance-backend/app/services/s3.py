import io
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import aioboto3
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile
from loguru import logger
from minio import Minio

from app.core.config import settings


class S3Service:
    """
    Service for interacting with S3 or MinIO
    """
    
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.use_minio = settings.USE_MINIO
        
        if self.use_minio:
            # Parse endpoint URL to get host and port
            endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
            self.minio_client = Minio(
                endpoint,
                access_key=settings.AWS_ACCESS_KEY_ID,
                secret_key=settings.AWS_SECRET_ACCESS_KEY,
                secure=settings.S3_ENDPOINT.startswith("https"),
            )
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        else:
            # Use AWS S3
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None,
            )
            self.s3_resource = boto3.resource(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None,
            )
            
            # Create async client for non-blocking operations
            self.session = aioboto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
    
    async def upload_file(self, file: UploadFile, object_name: Optional[str] = None) -> str:
        """
        Upload a file to S3/MinIO
        Returns the object name (S3 key)
        """
        if not object_name:
            object_name = file.filename
        
        try:
            file_content = await file.read()
            content_type = file.content_type or "application/octet-stream"
            
            if self.use_minio:
                # MinIO upload
                self.minio_client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    data=io.BytesIO(file_content),
                    length=len(file_content),
                    content_type=content_type,
                )
            else:
                # AWS S3 upload
                async with self.session.client("s3", endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None) as s3:
                    await s3.upload_fileobj(
                        io.BytesIO(file_content),
                        self.bucket_name,
                        object_name,
                        ExtraArgs={"ContentType": content_type},
                    )
            
            logger.info(f"Uploaded file {object_name} to {self.bucket_name}")
            return object_name
        
        except Exception as e:
            logger.error(f"Error uploading file to S3/MinIO: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
        finally:
            await file.seek(0)  # Reset file pointer
    
    async def download_file(self, object_name: str) -> Tuple[bytes, str]:
        """
        Download a file from S3/MinIO
        Returns the file content and content type
        """
        try:
            if self.use_minio:
                # MinIO download
                response = self.minio_client.get_object(self.bucket_name, object_name)
                content = response.read()
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                response.close()
                response.release_conn()
            else:
                # AWS S3 download
                async with self.session.client("s3", endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None) as s3:
                    response = await s3.get_object(Bucket=self.bucket_name, Key=object_name)
                    content = await response["Body"].read()
                    content_type = response.get("ContentType", "application/octet-stream")
            
            return content, content_type
        
        except Exception as e:
            logger.error(f"Error downloading file from S3/MinIO: {str(e)}")
            raise HTTPException(status_code=404, detail=f"File not found or error downloading: {str(e)}")
    
    async def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from S3/MinIO
        Returns True if successful
        """
        try:
            if self.use_minio:
                # MinIO delete
                self.minio_client.remove_object(self.bucket_name, object_name)
            else:
                # AWS S3 delete
                async with self.session.client("s3", endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None) as s3:
                    await s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            
            logger.info(f"Deleted file {object_name} from {self.bucket_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting file from S3/MinIO: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
    
    async def list_files(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in S3/MinIO bucket
        Returns a list of file information
        """
        try:
            files = []
            
            if self.use_minio:
                # MinIO list
                objects = self.minio_client.list_objects(self.bucket_name, prefix=prefix or "")
                for obj in objects:
                    files.append({
                        "key": obj.object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified,
                    })
            else:
                # AWS S3 list
                async with self.session.client("s3", endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT else None) as s3:
                    paginator = s3.get_paginator("list_objects_v2")
                    async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix or ""):
                        if "Contents" in page:
                            for obj in page["Contents"]:
                                files.append({
                                    "key": obj["Key"],
                                    "size": obj["Size"],
                                    "last_modified": obj["LastModified"],
                                })
            
            return files
        
        except Exception as e:
            logger.error(f"Error listing files from S3/MinIO: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


# Create a singleton instance
s3_service = S3Service()
