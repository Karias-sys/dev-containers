import os
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import yt_dlp
from tqdm import tqdm
import yaml
import json


class YouTubeDownloader:
    def __init__(self, config_file: str = "config.yaml"):
        self.config = self._load_config(config_file)
        self.logger = self._setup_logging()
        self.download_stats = {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0
        }
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        config_path = Path(config_file)
        if not config_path.exists():
            return self._get_default_config()
            
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() == '.yaml':
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    self.logger.warning(f"Unsupported config format: {config_path.suffix}")
                    return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            'default_quality': '720p',
            'default_format': 'mp4',
            'output_directory': './downloads',
            'max_concurrent_downloads': 3,
            'retry_attempts': 3,
            'timeout': 30,
            'extract_audio': False,
            'audio_format': 'mp3',
            'download_subtitles': False,
            'subtitle_languages': ['en'],
            'filename_template': '%(title)s.%(ext)s',
            'rate_limit': None
        }
    
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('youtube_downloader')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _create_output_directory(self, path: str) -> Path:
        output_path = Path(path)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def _get_ydl_opts(self, **kwargs) -> Dict[str, Any]:
        output_dir = self._create_output_directory(
            kwargs.get('output_directory', self.config['output_directory'])
        )
        
        opts = {
            'format': self._get_format_selector(kwargs),
            'outtmpl': str(output_dir / kwargs.get('filename_template', self.config['filename_template'])),
            'writesubtitles': kwargs.get('download_subtitles', self.config['download_subtitles']),
            'writeautomaticsub': kwargs.get('download_subtitles', self.config['download_subtitles']),
            'subtitleslangs': kwargs.get('subtitle_languages', self.config['subtitle_languages']),
            'ignoreerrors': True,
            'no_warnings': False,
            'extractaudio': kwargs.get('extract_audio', self.config['extract_audio']),
            'audioformat': kwargs.get('audio_format', self.config['audio_format']),
            'retries': kwargs.get('retry_attempts', self.config['retry_attempts']),
            'socket_timeout': kwargs.get('timeout', self.config['timeout']),
        }
        
        if self.config.get('rate_limit'):
            opts['ratelimit'] = self.config['rate_limit']
            
        return opts
    
    def _get_format_selector(self, kwargs: Dict[str, Any]) -> str:
        quality = kwargs.get('quality', self.config['default_quality'])
        format_type = kwargs.get('format', self.config['default_format'])
        
        if kwargs.get('extract_audio', self.config['extract_audio']):
            return 'bestaudio/best'
        
        if quality == 'best':
            return f'best[ext={format_type}]/best'
        elif quality == 'worst':
            return f'worst[ext={format_type}]/worst'
        else:
            height = quality.replace('p', '')
            return f'best[height<={height}][ext={format_type}]/best[height<={height}]/best'
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                downloaded = d.get('downloaded_bytes', 0)
                total = d['total_bytes']
                percent = (downloaded / total) * 100
                speed = d.get('speed')
                
                if speed is not None and speed > 0:
                    speed_mb = speed / 1024 / 1024
                    print(f"\rDownloading: {percent:.1f}% at {speed_mb:.1f} MB/s", end='')
                else:
                    print(f"\rDownloading: {percent:.1f}% at Unknown speed", end='')
            else:
                downloaded_mb = d.get('downloaded_bytes', 0) / 1024 / 1024
                print(f"\rDownloading: {downloaded_mb:.1f} MB", end='')
        elif d['status'] == 'finished':
            print(f"\nDownload completed: {d['filename']}")
            self.download_stats['successful_downloads'] += 1
            if 'total_bytes' in d:
                self.download_stats['total_size'] += d['total_bytes']
    
    def download_single(self, url: str, **kwargs) -> bool:
        try:
            self.logger.info(f"Starting download: {url}")
            self.download_stats['total_downloads'] += 1
            
            opts = self._get_ydl_opts(**kwargs)
            opts['progress_hooks'] = [self._progress_hook]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed for {url}: {e}")
            self.download_stats['failed_downloads'] += 1
            return False
    
    def download_batch(self, urls: List[str], **kwargs) -> Dict[str, bool]:
        results = {}
        
        for url in urls:
            self.logger.info(f"Processing batch download {len(results) + 1}/{len(urls)}")
            results[url] = self.download_single(url, **kwargs)
            
            if not results[url]:
                self.logger.warning(f"Failed to download: {url}")
                
        return results
    
    def download_playlist(self, playlist_url: str, **kwargs) -> bool:
        try:
            self.logger.info(f"Starting playlist download: {playlist_url}")
            
            opts = self._get_ydl_opts(**kwargs)
            opts['progress_hooks'] = [self._progress_hook]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([playlist_url])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Playlist download failed: {e}")
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'uploader': info.get('uploader'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'upload_date': info.get('upload_date'),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else None,
                    'formats': [{'format_id': f['format_id'], 'ext': f['ext'], 'height': f.get('height')} 
                               for f in info.get('formats', [])]
                }
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            return None
    
    def get_download_stats(self) -> Dict[str, Any]:
        return self.download_stats.copy()
    
    def reset_stats(self) -> None:
        self.download_stats = {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0
        }