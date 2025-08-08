// Global variables
let currentSessionId = null;
let currentVideoInfo = null;
let currentCutPoints = [];

// DOM elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const analysisSection = document.getElementById('analysisSection');
const timelineSection = document.getElementById('timelineSection');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');
    initializeEventListeners();
    updateSliderValues();
});

function initializeEventListeners() {
    // File upload
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);

    // Analysis settings
    document.getElementById('sensitivitySlider').addEventListener('input', updateSliderValues);
    document.getElementById('durationSlider').addEventListener('input', updateSliderValues);
    document.getElementById('ignoreCursor').addEventListener('change', updateCursorStatus);

    // Buttons
    document.getElementById('analyzeBtn').addEventListener('click', analyzeVideo);
    document.getElementById('processBtn').addEventListener('click', processVideo);
}

function updateSliderValues() {
    const sensitivity = document.getElementById('sensitivitySlider').value;
    const duration = document.getElementById('durationSlider').value;
    
    document.getElementById('sensitivityValue').textContent = sensitivity;
    document.getElementById('durationValue').textContent = duration;
}

function updateCursorStatus() {
    const isChecked = document.getElementById('ignoreCursor').checked;
    document.getElementById('cursorStatus').textContent = isChecked ? 'Enabled' : 'Disabled';
}

function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

async function handleFile(file) {
    console.log('Handling file:', file.name, file.type);
    
    if (!file.type.startsWith('video/')) {
        alert('Please select a valid video file.');
        return;
    }

    showUploadStatus();
    
    try {
        const formData = new FormData();
        formData.append('file', file);

        console.log('Uploading file...');
        const response = await fetch('http://localhost:8000/api/upload', {
            method: 'POST',
            body: formData,
        });

        console.log('Upload response status:', response.status);
        console.log('Upload response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Upload failed with status:', response.status, 'Error:', errorText);
            throw new Error(`Upload failed: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        console.log('Upload response data:', data);
        currentSessionId = data.session_id;

        // Get video info
        console.log('Getting video info for session:', data.session_id);
        const videoInfoResponse = await fetch(`http://localhost:8000/api/preview/${data.session_id}`);
        console.log('Video info response status:', videoInfoResponse.status);
        
        if (videoInfoResponse.ok) {
            const previewData = await videoInfoResponse.json();
            console.log('Video info response data:', previewData);
            currentVideoInfo = previewData.video_info;
            displayVideoInfo();
            showAnalysisSection();
        } else {
            const errorText = await videoInfoResponse.text();
            console.error('Failed to get video info:', videoInfoResponse.status, 'Error:', errorText);
        }

        hideUploadStatus();
    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed. Please try again.');
        hideUploadStatus();
    }
}

function showUploadStatus() {
    uploadStatus.classList.remove('hidden');
}

function hideUploadStatus() {
    uploadStatus.classList.add('hidden');
}

function displayVideoInfo() {
    console.log('Displaying video info:', currentVideoInfo);
    if (!currentVideoInfo) return;

    document.getElementById('videoName').textContent = currentVideoInfo.filename;
    document.getElementById('videoDuration').textContent = formatTime(currentVideoInfo.duration);
    document.getElementById('videoResolution').textContent = currentVideoInfo.resolution;
    document.getElementById('videoFps').textContent = `${currentVideoInfo.frame_rate.toFixed(1)} fps`;
    document.getElementById('videoSize').textContent = `${(currentVideoInfo.file_size / (1024 * 1024)).toFixed(1)} MB`;
    document.getElementById('totalDuration').textContent = formatTime(currentVideoInfo.duration);
}

function showAnalysisSection() {
    console.log('Showing analysis section');
    analysisSection.classList.remove('hidden');
}

function showTimelineSection() {
    console.log('Showing timeline section');
    timelineSection.classList.remove('hidden');
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

async function analyzeVideo() {
    if (!currentSessionId) {
        console.error('No session ID available');
        return;
    }

    showLoading('Analyzing Video', 'Detecting scene changes and cut points...');
    
    try {
        const sensitivity = document.getElementById('sensitivitySlider').value;
        const ignoreCursor = document.getElementById('ignoreCursor').checked;
        const minSegmentDuration = document.getElementById('durationSlider').value;

        console.log('Analyzing with settings:', { sensitivity, ignoreCursor, minSegmentDuration });

        const requestBody = {
            session_id: currentSessionId,
            sensitivity: parseFloat(sensitivity),
            ignore_cursor: ignoreCursor,
            min_segment_duration: parseFloat(minSegmentDuration)
        };

        console.log('Sending analysis request:', requestBody);

        const response = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        console.log('Analysis response status:', response.status);
        console.log('Analysis response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Analysis failed with status:', response.status, 'Error:', errorText);
            throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        console.log('Analysis response data:', data);
        
        if (data.cut_points && Array.isArray(data.cut_points)) {
            currentCutPoints = data.cut_points;
            console.log('Cut points received:', currentCutPoints.length);
            displayCutPoints();
            showTimelineSection();
        } else {
            console.error('No cut points in response or invalid format:', data);
            alert('Analysis completed but no cut points were detected.');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Analysis failed. Please try again.');
        hideLoading();
    }
}

function displayCutPoints() {
    console.log('Displaying cut points:', currentCutPoints);
    const cutPointsList = document.getElementById('cutPointsList');
    const cutPointsCount = document.getElementById('cutPointsCount');
    
    cutPointsCount.textContent = currentCutPoints.length;
    cutPointsList.innerHTML = '';

    currentCutPoints.forEach((point, index) => {
        const cutPointElement = document.createElement('div');
        cutPointElement.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors';
        
        cutPointElement.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium text-blue-600">${index + 1}</span>
                </div>
                <div>
                    <div class="font-medium text-gray-900">${formatTime(point.timestamp)}</div>
                    <div class="text-sm text-gray-500">
                        Frame ${point.frame_number} • ${point.change_type} • ${Math.round(point.confidence * 100)}% confidence
                    </div>
                </div>
            </div>
            <div class="text-sm text-gray-500">${point.description}</div>
        `;
        
        cutPointsList.appendChild(cutPointElement);
    });
}

async function processVideo() {
    if (!currentSessionId || currentCutPoints.length === 0) return;

    showLoading('Processing Video', 'Creating video segments and preparing download...');
    
    try {
        // Process the video
        const processResponse = await fetch('http://localhost:8000/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                cut_points: currentCutPoints
            }),
        });

        if (!processResponse.ok) {
            throw new Error('Processing failed');
        }

        const processData = await processResponse.json();
        console.log('Process response:', processData);
        
        // Get download information
        const downloadResponse = await fetch(`http://localhost:8000/api/download/${currentSessionId}`);
        if (downloadResponse.ok) {
            const downloadData = await downloadResponse.json();
            console.log('Download response:', downloadData);
            displayDownloadInfo(downloadData);
        }

        hideLoading();
    } catch (error) {
        console.error('Processing error:', error);
        alert('Processing failed. Please try again.');
        hideLoading();
    }
}

function displayDownloadInfo(downloadData) {
    document.getElementById('downloadLocation').textContent = `Location: ${downloadData.output_directory}`;
    
    const filesList = document.getElementById('filesList');
    filesList.innerHTML = '';
    
    downloadData.files.forEach(file => {
        const li = document.createElement('li');
        li.className = 'flex justify-between';
        li.innerHTML = `
            <span>${file.name}</span>
            <span>${(file.size / 1024).toFixed(1)} KB</span>
        `;
        filesList.appendChild(li);
    });
    
    document.getElementById('downloadInfo').classList.remove('hidden');
}

function showLoading(title, message) {
    document.getElementById('loadingTitle').textContent = title;
    document.getElementById('loadingMessage').textContent = message;
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
} 