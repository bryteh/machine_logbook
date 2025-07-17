import os
import tempfile
import logging
from typing import Optional, Tuple
from PIL import Image
import pillow_heif
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.base import ContentFile
from io import BytesIO
import subprocess
from pathlib import Path
import uuid
import mimetypes

# Optional imports for video processing
try:
    # import cv2
    import ffmpeg
    VIDEO_PROCESSING_AVAILABLE = True
    cv2 = None  # Disable OpenCV for now due to NumPy compatibility
except ImportError as e:
    VIDEO_PROCESSING_AVAILABLE = False
    cv2 = None
    ffmpeg = None

logger = logging.getLogger(__name__)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

class MediaProcessor:
    """
    Handles media file processing including:
    - HEIC to JPEG conversion
    - Image compression (50% quality)
    - Video conversion to 720p (if FFmpeg available)
    - File size optimization
    """
    
    # Maximum file size: 50MB (increased from 10MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Image settings
    IMAGE_QUALITY = 50  # 50% compression
    MAX_IMAGE_DIMENSION = 1920  # Max width/height for images
    
    # Video settings
    VIDEO_HEIGHT = 720  # 720p
    VIDEO_CRF = 28  # Compression level (lower = better quality, higher file size)
    
    def __init__(self):
        self.max_image_size = (1920, 1080)
        self.image_quality = 50
        
        # Find FFmpeg executable
        self.ffmpeg_path = self._find_ffmpeg()
        if self.ffmpeg_path:
            logger.info(f"FFmpeg found at: {self.ffmpeg_path}")
        else:
            logger.warning("FFmpeg not found - video processing will be disabled")
    
    def _find_ffmpeg(self):
        """Find FFmpeg executable in various possible locations"""
        possible_paths = [
            'ffmpeg',  # System PATH
            'ffmpeg.exe',  # Windows with .exe
            r'C:\ffmpeg\bin\ffmpeg.exe',  # Common Windows location
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Users\admin\Downloads\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe',
            '/usr/bin/ffmpeg',  # Common Linux location
            '/usr/local/bin/ffmpeg',  # Homebrew on macOS
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, '-version'], 
                                     capture_output=True, 
                                     text=True, 
                                     timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None
    
    def _generate_random_filename(self, original_filename):
        """Generate a random filename while preserving the extension"""
        # Get the file extension
        _, ext = os.path.splitext(original_filename)
        
        # Generate a random UUID-based filename
        random_name = str(uuid.uuid4()).replace('-', '')[:12]
        
        # Return the new filename with extension
        return f"{random_name}{ext}"
    
    def process_image(self, image_file):
        """Process and compress image files"""
        try:
            # Generate random filename
            random_filename = self._generate_random_filename(image_file.name)
            
            # Open and process the image
            with Image.open(image_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.size[0] > self.max_image_size[0] or img.size[1] > self.max_image_size[1]:
                    img.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                
                # Save to BytesIO with compression
                output = BytesIO()
                img.save(output, format='JPEG', quality=self.image_quality, optimize=True)
                output.seek(0)
                
                # Create Django file object with random name
                processed_file = ContentFile(output.getvalue(), name=random_filename)
                
                logger.info(f"Image processed: {random_filename}, size: {len(output.getvalue())} bytes")
                return processed_file
                
        except Exception as e:
            logger.error(f"Error processing image {image_file.name}: {str(e)}")
            # Return original file with random name if processing fails
            random_filename = self._generate_random_filename(image_file.name)
            return ContentFile(image_file.read(), name=random_filename)
    
    def process_video(self, video_file):
        """Process video files - currently disabled for deployment strategy"""
        try:
            # Generate random filename
            random_filename = self._generate_random_filename(video_file.name)
            
            # For now, just return the original video with random filename
            # Video compression will be handled in cloud deployment
            logger.info(f"Video file processed (no conversion): {random_filename}, size: {video_file.size} bytes")
            
            # Reset file pointer and return with random name
            video_file.seek(0)
            return ContentFile(video_file.read(), name=random_filename)
            
        except Exception as e:
            logger.error(f"Error processing video {video_file.name}: {str(e)}")
            # Return original file with random name if processing fails
            random_filename = self._generate_random_filename(video_file.name)
            video_file.seek(0)
            return ContentFile(video_file.read(), name=random_filename)
    
    def process_file(self, uploaded_file):
        """Main method to process uploaded files"""
        # Get file type
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        
        logger.info(f"Processing file: {uploaded_file.name}, size: {uploaded_file.size} bytes")
        
        if mime_type and mime_type.startswith('image/'):
            return self.process_image(uploaded_file)
        elif mime_type and mime_type.startswith('video/'):
            return self.process_video(uploaded_file)
        else:
            # For other file types, just rename with random filename
            random_filename = self._generate_random_filename(uploaded_file.name)
            logger.info(f"File processed (no conversion): {random_filename}, size: {uploaded_file.size} bytes")
            uploaded_file.seek(0)
            return ContentFile(uploaded_file.read(), name=random_filename)
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # Try to get image dimensions if it's an image
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    return {
                        'size': file_size,
                        'width': width,
                        'height': height,
                        'format': img.format
                    }
            except:
                # Not an image or can't open
                return {
                    'size': file_size,
                    'type': 'video' if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')) else 'unknown'
                }
                
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {'error': str(e)}
    
    def cleanup_temp_file(self, temp_path):
        """Clean up temporary files"""
        try:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary file {temp_path}: {str(e)}") 