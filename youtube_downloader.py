#!/usr/bin/env python3
"""
YouTube Video Downloader

A command-line tool for downloading YouTube videos, playlists, and channels
with support for various formats, qualities, and batch operations.

Usage:
    python youtube_downloader.py [URL]
    python youtube_downloader.py -f mp4 -q 720p [URL]
    python youtube_downloader.py --playlist [PLAYLIST_URL]
    python youtube_downloader.py --batch urls.txt

For more information, run:
    python youtube_downloader.py --help
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main

if __name__ == "__main__":
    main()