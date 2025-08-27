# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Video Scene Detector is a web-based application that automatically cuts screen recordings (MP4 files) into multiple segments whenever significant UI changes occur, while intelligently filtering out mouse cursor movements. The system uses PySceneDetect with OpenCV for computer vision analysis and provides a clean web interface built with vanilla JavaScript and FastAPI.

## Architecture

This is a full-stack application with:

### Backend (Python FastAPI)
- **FastAPI server** (`backend/main.py`) - RESTful API server on port 8000
- **Modular structure** under `backend/app/`:
  - `api/routes.py` - All API endpoints (/upload, /analyze, /process, /download)
  - `services/video_processor.py` - Core video analysis logic using PySceneDetect
  - `models/video.py` - Pydantic data models for requests/responses
  - `core/config.py` - Centralized configuration management
- **Session-based processing** - Each video upload creates a unique session ID
- **Computer vision pipeline** - Uses PySceneDetect ContentDetector with cursor masking

### Frontend (Vanilla JavaScript)
- **Single-page application** (`index.html`, `app.js`) - No framework dependencies
- **Drag-and-drop interface** with Tailwind CSS styling
- **Real-time progress tracking** during upload/analysis/processing
- **Deprecated React frontend** exists in `frontend/` but is not used

## Common Commands

### Backend Development
```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Test all imports (useful for debugging dependencies)
cd backend
python test_imports.py

# Start the FastAPI server
cd backend
python main.py
# Server runs on http://localhost:8000

# Start simple test server (minimal functionality)
python simple_server.py
```

### Frontend Development
```bash
# Serve the frontend (from root directory)
python -m http.server 8080
# Open http://localhost:8080 in browser

# Alternative: Open index.html directly in browser
```

### Full Development Workflow
```bash
# Terminal 1: Start backend
cd backend && python main.py

# Terminal 2: Serve frontend
python -m http.server 8080

# Access at http://localhost:8080
```

### Testing & Debugging
```bash
# Test PySceneDetect functionality
cd backend
python debug_pyscenedetect.py

# Run import tests
cd backend
python test_imports.py

# Enable debug mode
cd backend
set DEBUG=1  # Windows
python main.py
```

## System Requirements

### Critical Dependencies
- **Python 3.13+** - Required for backend
- **FFmpeg** - Must be in system PATH for video processing
  - Windows: Download from ffmpeg.org, add to PATH
  - Install via Chocolatey: `choco install ffmpeg`
- **PySceneDetect 0.6.2** - Scene detection algorithm
- **OpenCV 4.9+** - Computer vision operations

### Verify Dependencies
```bash
# Check FFmpeg installation
ffmpeg -version

# Check Python version
python --version

# Test all imports
cd backend && python test_imports.py
```

## Development Patterns

### Session Management
- Each video upload creates a unique session ID (UUID4)
- Sessions store: video metadata, detected cut points, processing status
- Session data persists in memory during server runtime
- Access via `VideoProcessor.get_session(session_id)`

### Video Processing Pipeline
1. **Upload** - File validation, metadata extraction via OpenCV
2. **Analysis** - PySceneDetect ContentDetector with configurable sensitivity
3. **Cursor Masking** - Optional filtering of mouse movement areas
4. **Segmentation** - FFmpeg-based video cutting at detected points
5. **Download** - Processed segments saved to `download/` folder

### API Endpoint Flow
- `POST /api/upload` → Session creation, video info extraction
- `GET /api/preview/{session_id}` → Retrieve video metadata
- `POST /api/analyze` → Run scene detection algorithm
- `POST /api/process` → Generate video segments
- `GET /api/download/{session_id}` → Access processed files

### Configuration Management
All settings centralized in `backend/app/core/config.py`:
- File size limits, allowed extensions
- PySceneDetect thresholds and sensitivity mappings
- Session timeouts, directory paths
- CORS settings for cross-origin requests

## Key Files and Their Roles

### Core Backend Files
- `backend/main.py` - Application entry point, middleware setup
- `backend/app/services/video_processor.py` - Main business logic
- `backend/app/api/routes.py` - API endpoint definitions
- `backend/app/core/config.py` - Configuration management

### Frontend Files
- `index.html` - Main application interface
- `app.js` - All frontend logic, API communication
- `frontend/` - Deprecated React version (not in use)

### Utility Scripts
- `backend/test_imports.py` - Dependency verification
- `backend/debug_pyscenedetect.py` - PySceneDetect testing
- `simple_server.py` - Minimal server for testing

## Common Issues & Solutions

### FFmpeg Not Found
```bash
# Verify installation
ffmpeg -version

# Windows with Chocolatey
choco install ffmpeg

# Add to PATH manually on Windows
# C:\ffmpeg\bin must be in system PATH
```

### Import Errors
```bash
# Test all dependencies
cd backend
python test_imports.py

# Common fix: reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### CORS Issues
- Backend runs on port 8000, frontend on 8080
- CORS middleware configured for `*` origins in development
- Check `backend/app/core/config.py` for CORS settings

### Scene Detection Not Working
- Adjust sensitivity in UI (0.1-1.0 range)
- Check video format compatibility (MP4, AVI, MOV, MKV)
- Verify FFmpeg can process the specific video file
- Try disabling cursor filtering for static screen recordings

## Project Structure Understanding

The codebase follows a clean separation between frontend and backend with session-based state management. The PySceneDetect integration uses ContentDetector with dynamic thresholds based on user sensitivity settings, and includes sophisticated cursor movement masking for screen recordings. The frontend is intentionally framework-free for simplicity and direct API communication.
