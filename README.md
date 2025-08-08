# Video Scene Detector

A web-based application that automatically cuts screen recordings (MP4 files) into multiple segments whenever a significant UI change occurs, while ignoring mouse cursor movements.

## Features

- **Automatic Scene Detection**: Uses PySceneDetect library to detect UI changes in screen recordings
- **Cursor Movement Filtering**: Ignores mouse cursor movements to focus on actual UI changes
- **High-Quality Output**: Maintains original video quality, aspect ratio, and resolution
- **Interactive Timeline**: Preview detected cut points with frame-level precision
- **Manual Adjustment**: Fine-tune cut points if automatic detection is inaccurate
- **Modern Web Interface**: Clean, responsive UI built with HTML, CSS, and vanilla JavaScript
- **Multiple Output Formats**: Creates individual MP4 segments and detailed log files

## Technology Stack

### Backend
- **Python 3.13+**
- **FastAPI** - Modern, fast web framework
- **OpenCV** - Computer vision and image processing
- **PySceneDetect** - Scene detection library
- **FFmpeg** - Video processing and encoding

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Styling with Tailwind CSS (CDN)
- **Vanilla JavaScript** - No framework dependencies
- **Font Awesome** - Icons

## Installation

### Prerequisites

1. **Python 3.13 or higher**
2. **FFmpeg** - Required for video processing

### FFmpeg Installation

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Restart your terminal/command prompt

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### Project Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/video-scene-detector.git
cd video-scene-detector
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Start the backend server**
```bash
python main.py
```

The server will start on `http://localhost:8000`

4. **Open the frontend**
- Open `index.html` in your web browser
- Or serve it with a simple HTTP server:
```bash
python -m http.server 8080
```
Then visit `http://localhost:8080`

## Usage

1. **Upload Video**: Drag and drop or click to select a video file (MP4, AVI, MOV, WMV)

2. **Configure Analysis Settings**:
   - **Sensitivity**: Adjust detection sensitivity (0.1 - 1.0)
   - **Ignore Cursor**: Toggle cursor movement filtering
   - **Min Segment Duration**: Set minimum segment length (0.5 - 5.0 seconds)

3. **Analyze Video**: Click "Analyze Video" to detect cut points

4. **Review Results**: View detected cut points in the timeline

5. **Process & Download**: Click "Process & Download" to create video segments

6. **Access Files**: Find processed files in the `download/` folder

## API Endpoints

- `POST /api/upload` - Upload video file
- `GET /api/preview/{session_id}` - Get video information
- `POST /api/analyze` - Analyze video for cut points
- `POST /api/process` - Process video into segments
- `GET /api/download/{session_id}` - Get download information

## Project Structure

```
video-scene-detector/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── core/
│   │   │   └── config.py          # Configuration
│   │   ├── models/
│   │   │   └── video.py           # Data models
│   │   └── services/
│   │       └── video_processor.py # Video processing logic
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Python dependencies
│   └── uploads/                   # Uploaded video storage
├── frontend/                      # React frontend (deprecated)
├── download/                      # Processed video segments
├── index.html                     # Main frontend file
├── app.js                         # Frontend JavaScript
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Configuration

### Backend Configuration

Edit `backend/app/core/config.py` to modify:
- Session timeout
- File upload limits
- Processing parameters

### Frontend Configuration

Edit `app.js` to modify:
- API endpoint URLs
- UI behavior
- Error handling

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in your PATH
   - Check installation with `ffmpeg -version`

2. **Upload fails**
   - Check file format (MP4, AVI, MOV, WMV)
   - Ensure file size is reasonable (< 1GB recommended)

3. **Analysis fails**
   - Verify video file is not corrupted
   - Try adjusting sensitivity settings
   - Check console for error messages

4. **No cut points detected**
   - Increase sensitivity setting
   - Ensure video has clear UI changes
   - Check if cursor filtering is too aggressive

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export DEBUG=1
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect) - Scene detection library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [FFmpeg](https://ffmpeg.org/) - Video processing toolkit

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Open an issue on GitHub with detailed information 