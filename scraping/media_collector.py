"""
Media Collector Module

This module provides functionality for collecting, filtering, and downloading media files
from Threads.net during the scraping process. It monitors network requests to capture
media URLs and organizes downloads into structured folders.
"""

import os
import re
import asyncio
import aiohttp
import aiofiles
from urllib.parse import urlparse, unquote
from typing import Set, Dict, List, Optional, Tuple
import mimetypes
from datetime import datetime
import hashlib
import json
from pathlib import Path


class MediaCollector:
    """
    Handles media collection, filtering, and downloading for the Threads scraper.
    
    Features:
    - Network request monitoring and filtering
    - Media type detection and validation
    - Organized folder structure creation
    - Concurrent download management
    - Progress tracking and error handling
    """
    
    # Supported media file extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'}
    VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v'}
    
    # Media MIME types
    IMAGE_MIMETYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 
        'image/bmp', 'image/svg+xml', 'image/x-icon'
    }
    VIDEO_MIMETYPES = {
        'video/mp4', 'video/webm', 'video/quicktime', 'video/avi',
        'video/x-msvideo', 'video/x-matroska', 'video/x-flv'
    }
    
    def __init__(self, base_output_dir: str = "data", max_file_size: int = 50*1024*1024,
                 concurrent_downloads: int = 5, collect_images: bool = True,
                 collect_videos: bool = True):
        """
        Initialize the MediaCollector.
        
        Args:
            base_output_dir (str): Base directory for media storage
            max_file_size (int): Maximum file size in bytes (default: 50MB)
            concurrent_downloads (int): Number of concurrent downloads
            collect_images (bool): Whether to collect image files
            collect_videos (bool): Whether to collect video files
        """
        self.base_output_dir = Path(base_output_dir)
        self.max_file_size = max_file_size
        self.concurrent_downloads = concurrent_downloads
        self.collect_images = collect_images
        self.collect_videos = collect_videos
        
        # Track collected media URLs to avoid duplicates
        self.collected_urls: Set[str] = set()
        self.media_metadata: Dict[str, Dict] = {}
        
        # Download statistics
        self.download_stats = {
            'total_discovered': 0,
            'total_downloaded': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'bytes_downloaded': 0
        }
        
        # Semaphore for controlling concurrent downloads
        self.download_semaphore = asyncio.Semaphore(concurrent_downloads)
    
    def is_media_url(self, url: str, content_type: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check if a URL points to a media file.
        
        Args:
            url (str): URL to check
            content_type (str, optional): Content-Type header if available
            
        Returns:
            Tuple[bool, str]: (is_media, media_type) where media_type is 'image' or 'video'
        """
        # Clean the URL
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Check by content type first (most reliable)
        if content_type:
            content_type = content_type.lower().split(';')[0].strip()
            if self.collect_images and content_type in self.IMAGE_MIMETYPES:
                return True, 'image'
            if self.collect_videos and content_type in self.VIDEO_MIMETYPES:
                return True, 'video'
        
        # Check by file extension
        for ext in self.IMAGE_EXTENSIONS:
            if path.endswith(ext):
                return self.collect_images, 'image'
        
        for ext in self.VIDEO_EXTENSIONS:
            if path.endswith(ext):
                return self.collect_videos, 'video'
        
        # Check for common image/video URL patterns
        if self.collect_images and self._is_image_url_pattern(url):
            return True, 'image'
        if self.collect_videos and self._is_video_url_pattern(url):
            return True, 'video'
        
        return False, ''
    
    def _is_image_url_pattern(self, url: str) -> bool:
        """Check if URL matches common image URL patterns."""
        image_patterns = [
            r'/image/',
            r'/img/',
            r'/photo/',
            r'/picture/',
            r'/avatar/',
            r'/profile.*\.(jpg|jpeg|png|gif|webp)',
            r'\.cdninstagram\.com.*\.(jpg|jpeg|png|gif|webp)',
            r'scontent.*\.(jpg|jpeg|png|gif|webp)'
        ]
        
        for pattern in image_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _is_video_url_pattern(self, url: str) -> bool:
        """Check if URL matches common video URL patterns."""
        video_patterns = [
            r'/video/',
            r'/videos/',
            r'/media.*\.(mp4|webm|mov)',
            r'\.cdninstagram\.com.*\.(mp4|webm)',
            r'scontent.*\.(mp4|webm)'
        ]
        
        for pattern in video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def add_media_url(self, url: str, content_type: Optional[str] = None,
                     post_id: Optional[str] = None, context: str = "unknown") -> bool:
        """
        Add a media URL to the collection queue.
        
        Args:
            url (str): Media URL to add
            content_type (str, optional): Content-Type header
            post_id (str, optional): Associated post ID
            context (str): Context where the media was found
            
        Returns:
            bool: True if URL was added, False if skipped
        """
        # Check if this is a media URL
        is_media, media_type = self.is_media_url(url, content_type)
        if not is_media:
            return False
        
        # Check for duplicates
        if url in self.collected_urls:
            return False
        
        # Add to collection
        self.collected_urls.add(url)
        self.media_metadata[url] = {
            'type': media_type,
            'content_type': content_type,
            'post_id': post_id,
            'context': context,
            'discovered_at': datetime.now().isoformat(),
            'downloaded': False,
            'file_path': None,
            'file_size': None,
            'download_error': None
        }
        
        self.download_stats['total_discovered'] += 1
        return True
    
    def create_user_directory(self, username: str) -> Path:
        """
        Create directory structure for a user.
        
        Args:
            username (str): Username to create directories for
            
        Returns:
            Path: Path to the user's base directory
        """
        user_dir = self.base_output_dir / username
        images_dir = user_dir / "images"
        videos_dir = user_dir / "videos"
        
        # Create directories
        user_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        
        return user_dir
    
    def _generate_filename(self, url: str, media_type: str, content_type: Optional[str] = None) -> str:
        """
        Generate a safe filename from URL and metadata.
        
        Args:
            url (str): Original URL
            media_type (str): Type of media ('image' or 'video')
            content_type (str, optional): Content-Type header
            
        Returns:
            str: Safe filename
        """
        # Parse URL to get the original filename
        parsed_url = urlparse(url)
        original_name = os.path.basename(parsed_url.path)
        
        # Remove query parameters and decode
        original_name = unquote(original_name.split('?')[0])
        
        # If no filename or extension, generate one
        if not original_name or '.' not in original_name:
            # Generate hash-based filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            
            # Determine extension from content type or media type
            if content_type:
                ext = mimetypes.guess_extension(content_type.split(';')[0].strip())
                if not ext:
                    ext = '.jpg' if media_type == 'image' else '.mp4'
            else:
                ext = '.jpg' if media_type == 'image' else '.mp4'
            
            original_name = f"{url_hash}{ext}"
        
        # Sanitize filename
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
        safe_name = safe_name[:100]  # Limit length
        
        return safe_name
    
    async def download_media(self, url: str, user_dir: Path, session: aiohttp.ClientSession) -> bool:
        """
        Download a single media file.
        
        Args:
            url (str): URL to download
            user_dir (Path): User's base directory
            session (aiohttp.ClientSession): HTTP session
            
        Returns:
            bool: True if successful, False otherwise
        """
        async with self.download_semaphore:
            try:
                metadata = self.media_metadata[url]
                media_type = metadata['type']
                
                # Determine target directory
                target_dir = user_dir / ('images' if media_type == 'image' else 'videos')
                
                # Generate filename
                filename = self._generate_filename(url, media_type, metadata.get('content_type'))
                file_path = target_dir / filename
                
                # Check if file already exists
                if file_path.exists():
                    print(f"Skipping {filename} - already exists")
                    metadata['downloaded'] = True
                    metadata['file_path'] = str(file_path)
                    self.download_stats['total_skipped'] += 1
                    return True
                
                # Download the file
                print(f"Downloading {filename}...")
                async with session.get(url) as response:
                    if response.status != 200:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
                    
                    # Check file size
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_file_size:
                        raise ValueError(f"File too large: {content_length} bytes")
                    
                    # Download and save
                    async with aiofiles.open(file_path, 'wb') as f:
                        downloaded_bytes = 0
                        async for chunk in response.content.iter_chunked(8192):
                            downloaded_bytes += len(chunk)
                            if downloaded_bytes > self.max_file_size:
                                raise ValueError(f"File too large: {downloaded_bytes} bytes")
                            await f.write(chunk)
                    
                    # Update metadata
                    metadata['downloaded'] = True
                    metadata['file_path'] = str(file_path)
                    metadata['file_size'] = downloaded_bytes
                    
                    self.download_stats['total_downloaded'] += 1
                    self.download_stats['bytes_downloaded'] += downloaded_bytes
                    
                    print(f"✅ Downloaded {filename} ({downloaded_bytes} bytes)")
                    return True
                    
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Failed to download {url}: {error_msg}")
                
                # Update metadata with error
                self.media_metadata[url]['download_error'] = error_msg
                self.download_stats['total_failed'] += 1
                return False
    
    async def download_all_media(self, username: str) -> Dict:
        """
        Download all collected media for a user.
        
        Args:
            username (str): Username to download media for
            
        Returns:
            Dict: Download statistics and results
        """
        if not self.collected_urls:
            print("No media URLs to download")
            return self.download_stats
        
        print(f"Starting download of {len(self.collected_urls)} media files for {username}...")
        
        # Create user directory
        user_dir = self.create_user_directory(username)
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Create download tasks
            tasks = [
                self.download_media(url, user_dir, session)
                for url in self.collected_urls
            ]
            
            # Execute downloads concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save metadata
        await self._save_media_metadata(user_dir)
        
        # Print summary
        stats = self.download_stats
        print(f"\n📊 Download Summary for {username}:")
        print(f"   Total discovered: {stats['total_discovered']}")
        print(f"   Successfully downloaded: {stats['total_downloaded']}")
        print(f"   Failed downloads: {stats['total_failed']}")
        print(f"   Skipped (existing): {stats['total_skipped']}")
        print(f"   Total bytes downloaded: {stats['bytes_downloaded']:,}")
        
        return stats
    
    async def _save_media_metadata(self, user_dir: Path):
        """Save media metadata to JSON file."""
        metadata_file = user_dir / "media_metadata.json"
        
        try:
            async with aiofiles.open(metadata_file, 'w') as f:
                await f.write(json.dumps(self.media_metadata, indent=2))
            print(f"💾 Media metadata saved to {metadata_file}")
        except Exception as e:
            print(f"Warning: Failed to save media metadata: {e}")
    
    def reset_collection(self):
        """Reset the collector for a new user."""
        self.collected_urls.clear()
        self.media_metadata.clear()
        self.download_stats = {
            'total_discovered': 0,
            'total_downloaded': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'bytes_downloaded': 0
        }