# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a dev-containers tutorial environment with a Product Requirements Document (PRD) for a YouTube Video Downloader project. The repository currently contains:

- `Readme.md` - Brief description indicating this is a dev containers tutorial folder
- `prd.txt` - Comprehensive PRD for a Python-based YouTube video downloader CLI tool

## Development Context

This appears to be a learning/tutorial environment for VS Code dev containers. The PRD outlines a YouTube video downloader project with the following key technical specifications:

### Technology Stack (from PRD)
- **Language**: Python 3.8+
- **Primary Library**: yt-dlp
- **Dependencies**: requests, ffmpeg, argparse, configparser
- **Cross-platform**: Windows, macOS, Linux

### Key Architecture Components (from PRD)
- Command-line interface with argparse
- Configuration management (YAML/JSON)
- Batch processing capabilities
- Error handling with retry mechanisms
- Progress tracking and logging
- Multiple format/quality support

## Development Notes

Since this is currently a tutorial/planning environment with no actual code implementation:

1. **Future Development**: When implementing the YouTube downloader, follow the detailed specifications in `prd.txt`
2. **Testing**: The PRD specifies unit tests, integration tests, and cross-platform compatibility testing
3. **Dependencies**: Will require FFmpeg installation for video/audio processing
4. **Security**: Must respect YouTube's Terms of Service and include copyright compliance warnings

## Development Environment

This repository is set up for VS Code dev containers development as indicated by the Readme.md reference to the VS Code dev containers tutorial.

## Workflow Guidelines

- Always use context 7 to check up to date documentation and latest version of libraries and language