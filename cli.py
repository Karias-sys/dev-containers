import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
from downloader import YouTubeDownloader


def setup_logging(level: str = 'INFO') -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('youtube_downloader.log')
        ]
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='YouTube Video Downloader - Download videos, playlists, and channels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -f mp4 -q 720p https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s --playlist https://www.youtube.com/playlist?list=PLrSOXFDHBtfHD_i_-WKm4_ZgJcUpMV8T7
  %(prog)s --batch urls.txt
  %(prog)s --extract-audio --audio-format mp3 https://www.youtube.com/watch?v=dQw4w9WgXcQ
        '''
    )
    
    # URL arguments
    parser.add_argument(
        'url',
        nargs='?',
        help='YouTube video URL to download'
    )
    
    # Format and quality options
    parser.add_argument(
        '-f', '--format',
        choices=['mp4', 'mkv', 'webm', 'best'],
        default='mp4',
        help='Video format (default: mp4)'
    )
    
    parser.add_argument(
        '-q', '--quality',
        choices=['144p', '240p', '360p', '480p', '720p', '1080p', 'best', 'worst'],
        default='720p',
        help='Video quality (default: 720p)'
    )
    
    # Audio options
    parser.add_argument(
        '--extract-audio',
        action='store_true',
        help='Extract audio only'
    )
    
    parser.add_argument(
        '--audio-format',
        choices=['mp3', 'm4a', 'wav'],
        default='mp3',
        help='Audio format when extracting audio (default: mp3)'
    )
    
    # Batch and playlist options
    parser.add_argument(
        '--batch',
        type=str,
        help='File containing URLs to download (one per line)'
    )
    
    parser.add_argument(
        '--playlist',
        action='store_true',
        help='Download entire playlist'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output-directory',
        type=str,
        default='./downloads',
        help='Output directory for downloads (default: ./downloads)'
    )
    
    parser.add_argument(
        '--filename-template',
        type=str,
        default='%(title)s.%(ext)s',
        help='Filename template (default: %(title)s.%(ext)s)'
    )
    
    # Subtitle options
    parser.add_argument(
        '--download-subtitles',
        action='store_true',
        help='Download subtitles'
    )
    
    parser.add_argument(
        '--subtitle-languages',
        nargs='+',
        default=['en'],
        help='Subtitle languages to download (default: en)'
    )
    
    # Advanced options
    parser.add_argument(
        '--retry-attempts',
        type=int,
        default=3,
        help='Number of retry attempts (default: 3)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Socket timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=str,
        help='Rate limit (e.g., 1M for 1MB/s)'
    )
    
    # Configuration and logging
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Information options
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show video information without downloading'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show download statistics'
    )
    
    return parser.parse_args()


def load_batch_urls(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except FileNotFoundError:
        print(f"Error: Batch file '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading batch file: {e}")
        sys.exit(1)


def print_video_info(downloader: YouTubeDownloader, url: str) -> None:
    info = downloader.get_video_info(url)
    if info:
        print(f"Title: {info['title']}")
        print(f"Uploader: {info['uploader']}")
        print(f"Duration: {info['duration']} seconds")
        print(f"View Count: {info['view_count']:,}")
        print(f"Upload Date: {info['upload_date']}")
        print(f"Description: {info['description']}")
        print("\nAvailable formats:")
        for fmt in info['formats'][:10]:  # Show first 10 formats
            print(f"  {fmt['format_id']}: {fmt['ext']} ({fmt.get('height', 'N/A')}p)")
    else:
        print("Failed to retrieve video information.")


def print_download_stats(downloader: YouTubeDownloader) -> None:
    stats = downloader.get_download_stats()
    print("\nDownload Statistics:")
    print(f"Total Downloads: {stats['total_downloads']}")
    print(f"Successful: {stats['successful_downloads']}")
    print(f"Failed: {stats['failed_downloads']}")
    print(f"Total Size: {stats['total_size'] / 1024 / 1024:.2f} MB")
    if stats['total_downloads'] > 0:
        success_rate = (stats['successful_downloads'] / stats['total_downloads']) * 100
        print(f"Success Rate: {success_rate:.1f}%")


def main():
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Validate arguments
    if not args.url and not args.batch:
        print("Error: Please provide either a URL or a batch file.")
        sys.exit(1)
    
    # Initialize downloader
    try:
        downloader = YouTubeDownloader(args.config)
    except Exception as e:
        print(f"Error initializing downloader: {e}")
        sys.exit(1)
    
    # Handle info request
    if args.info:
        if args.url:
            print_video_info(downloader, args.url)
        else:
            print("Error: --info requires a URL")
            sys.exit(1)
        return
    
    # Prepare download options
    download_opts = {
        'format': args.format,
        'quality': args.quality,
        'extract_audio': args.extract_audio,
        'audio_format': args.audio_format,
        'output_directory': args.output_directory,
        'filename_template': args.filename_template,
        'download_subtitles': args.download_subtitles,
        'subtitle_languages': args.subtitle_languages,
        'retry_attempts': args.retry_attempts,
        'timeout': args.timeout,
    }
    
    if args.rate_limit:
        download_opts['rate_limit'] = args.rate_limit
    
    # Execute downloads
    try:
        if args.batch:
            urls = load_batch_urls(args.batch)
            print(f"Starting batch download of {len(urls)} URLs...")
            results = downloader.download_batch(urls, **download_opts)
            
            print(f"\nBatch download completed:")
            for url, success in results.items():
                status = "✓" if success else "✗"
                print(f"{status} {url}")
                
        elif args.playlist:
            print("Starting playlist download...")
            success = downloader.download_playlist(args.url, **download_opts)
            if success:
                print("Playlist download completed successfully!")
            else:
                print("Playlist download failed.")
                sys.exit(1)
                
        else:
            print("Starting single video download...")
            success = downloader.download_single(args.url, **download_opts)
            if success:
                print("Download completed successfully!")
            else:
                print("Download failed.")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during download: {e}")
        sys.exit(1)
    
    # Show statistics if requested
    if args.stats:
        print_download_stats(downloader)


if __name__ == "__main__":
    main()