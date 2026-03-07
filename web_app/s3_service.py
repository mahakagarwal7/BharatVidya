# web_app/s3_service.py
"""
AWS S3 service for video storage.
Videos are uploaded to S3 and served via presigned URLs or CloudFront.
"""

import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from datetime import datetime


class S3Service:
    """
    Handles video uploads to AWS S3.
    
    Environment variables:
        AWS_ACCESS_KEY_ID: AWS access key
        AWS_SECRET_ACCESS_KEY: AWS secret key
        AWS_REGION: AWS region (default: us-east-1)
        S3_BUCKET_NAME: S3 bucket for videos
        CLOUDFRONT_DOMAIN: Optional CloudFront distribution domain
    """
    
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "edugen-videos")
        self.cloudfront_domain = os.getenv("CLOUDFRONT_DOMAIN")
        
        
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        self._enabled = self._check_enabled()
    
    def _check_enabled(self) -> bool:
        """Check if S3 is properly configured"""
        if not os.getenv("AWS_ACCESS_KEY_ID"):
            print("⚠️ S3 disabled: AWS_ACCESS_KEY_ID not set")
            return False
        if not os.getenv("AWS_SECRET_ACCESS_KEY"):
            print("⚠️ S3 disabled: AWS_SECRET_ACCESS_KEY not set")
            return False
        return True
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    def upload_video(
        self, 
        local_path: str, 
        job_id: str,
        content_type: str = "video/mp4"
    ) -> Optional[str]:
        """
        Upload a video file to S3.
        
        Args:
            local_path: Path to local video file
            job_id: Job ID to use in S3 key
            content_type: MIME type of the video
        
        Returns:
            S3 URL or CloudFront URL if configured, None on failure
        """
        if not self._enabled:
            return None
        
        if not os.path.exists(local_path):
            print(f"❌ File not found: {local_path}")
            return None
        
       
        date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        filename = os.path.basename(local_path)
        s3_key = f"videos/{date_prefix}/{job_id}_{filename}"
        
        try:
            print(f"📤 Uploading to S3: {s3_key}")
            
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "max-age=31536000",  # 1 year cache
                }
            )
            
            if self.cloudfront_domain:
                url = f"https://{self.cloudfront_domain}/{s3_key}"
            else:
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            
            print(f"✅ Uploaded: {url}")
            return url
            
        except ClientError as e:
            print(f"❌ S3 upload failed: {e}")
            return None
    
    def get_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary access.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Presigned URL or None on failure
        """
        if not self._enabled:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"❌ Failed to generate presigned URL: {e}")
            return None
    
    def delete_video(self, s3_key: str) -> bool:
        """
        Delete a video from S3.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            True on success, False on failure
        """
        if not self._enabled:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"❌ Failed to delete from S3: {e}")
            return False
    
    def list_videos(self, prefix: str = "videos/", max_keys: int = 100) -> list:
        """
        List videos in S3 bucket.
        
        Args:
            prefix: S3 key prefix to filter
            max_keys: Maximum number of objects to return
        
        Returns:
            List of S3 object keys
        """
        if not self._enabled:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            return [obj["Key"] for obj in response.get("Contents", [])]
            
        except ClientError as e:
            print(f"❌ Failed to list S3 objects: {e}")
            return []


s3_service = S3Service()
