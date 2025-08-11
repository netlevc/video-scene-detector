// This is the main JavaScript file for the Video Scene Detector web interface
// It handles all the interactive functionality like file uploads, API calls, and UI updates

// Global variables to store the current state of the application
let currentSessionId = null;  // Unique identifier for the current video processing session
let currentVideoInfo = null;  // Information about the currently uploaded video
let currentCutPoints = [];    // Array of detected cut points in the video

// Get references to important HTML elements that we'll need to update
const dropZone = document.getElementById('dropZone');           // The drag-and-drop area
const fileInput = document.getElementById('fileInput');         // Hidden file input element
const uploadStatus = document.getElementById('uploadStatus');   // Upload progress indicator
const analysisSection = document.getElementById('analysisSection');  // Analysis settings section
const timelineSection = document.getElementById('timelineSection');  // Results display section
const loadingOverlay = document.getElementById('loadingOverlay');    // Full-screen loading overlay

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('App initialized');  // Log that the app has started
    initializeEventListeners();      // Set up all the event handlers
    updateSliderValues();            // Update the display values for sliders
});

// Set up all the event listeners for user interactions
function initializeEventListeners() {
    // File upload event handlers
    dropZone.addEventListener('click', () => fileInput.click());  // Click drop zone to open file picker
    dropZone.addEventListener('dragover', handleDragOver);        // Handle drag over the drop zone
    dropZone.addEventListener('dragleave', handleDragLeave);      // Handle leaving the drop zone
    dropZone.addEventListener('drop', handleDrop);               // Handle dropping files
    fileInput.addEventListener('change', handleFileSelect);      // Handle file selection via file picker

    // Analysis settings event handlers
    document.getElementById('sensitivitySlider').addEventListener('input', updateSliderValues);  // Update sensitivity display
    document.getElementById('durationSlider').addEventListener('input', updateSliderValues);     // Update duration display
    document.getElementById('ignoreCursor').addEventListener('change', updateCursorStatus);      // Update cursor status display

    // Button event handlers
    document.getElementById('analyzeBtn').addEventListener('click', analyzeVideo);  // Start video analysis
    document.getElementById('processBtn').addEventListener('click', processVideo);  // Start video processing
}

// Update the display values for the sliders when they change
function updateSliderValues() {
    const sensitivity = document.getElementById('sensitivitySlider').value;  // Get current sensitivity value
    const duration = document.getElementById('durationSlider').value;        // Get current duration value
    
    // Update the display text to show current values
    document.getElementById('sensitivityValue').textContent = sensitivity;
    document.getElementById('durationValue').textContent = duration;
}

// Update the cursor status display when the toggle changes
function updateCursorStatus() {
    const isChecked = document.getElementById('ignoreCursor').checked;  // Get toggle state
    document.getElementById('cursorStatus').textContent = isChecked ? 'Enabled' : 'Disabled';  // Update display text
}

// Handle when a user drags a file over the drop zone
function handleDragOver(e) {
    e.preventDefault();  // Prevent default browser behavior
    dropZone.classList.add('dragover');  // Add visual feedback (blue border)
}

// Handle when a user leaves the drop zone while dragging
function handleDragLeave(e) {
    e.preventDefault();  // Prevent default browser behavior
    dropZone.classList.remove('dragover');  // Remove visual feedback
}

// Handle when a user drops files onto the drop zone
function handleDrop(e) {
    e.preventDefault();  // Prevent default browser behavior
    dropZone.classList.remove('dragover');  // Remove visual feedback
    
    const files = e.dataTransfer.files;  // Get the dropped files
    if (files.length > 0) {
        handleFile(files[0]);  // Process the first dropped file
    }
}

// Handle when a user selects a file via the file picker
function handleFileSelect(e) {
    const file = e.target.files[0];  // Get the selected file
    if (file) {
        handleFile(file);  // Process the selected file
    }
}

// Main function to handle file processing (both drag-drop and file picker)
async function handleFile(file) {
    console.log('Handling file:', file.name, file.type);  // Log file information
    
    // Check if the file is actually a video
    if (!file.type.startsWith('video/')) {
        alert('Please select a valid video file.');  // Show error message
        return;
    }

    showUploadStatus();  // Show upload progress indicator
    
    try {
        // Prepare the file for upload
        const formData = new FormData();  // Create form data for file upload
        formData.append('file', file);    // Add the file to the form data

        console.log('Uploading file...');  // Log upload start
        
        // Send the file to the backend server
        const response = await fetch('http://localhost:8000/api/upload', {
            method: 'POST',  // Use POST method for file upload
            body: formData,  // Send the file data
        });

        console.log('Upload response status:', response.status);  // Log response status
        console.log('Upload response headers:', response.headers);  // Log response headers

        // Check if the upload was successful
        if (!response.ok) {
            const errorText = await response.text();  // Get error message from server
            console.error('Upload failed with status:', response.status, 'Error:', errorText);
            throw new Error(`Upload failed: ${response.status} - ${errorText}`);
        }

        // Parse the response data
        const data = await response.json();  // Convert response to JavaScript object
        console.log('Upload response data:', data);
        currentSessionId = data.session_id;  // Store the session ID for later use

        // Get video information from the server
        console.log('Getting video info for session:', data.session_id);
        const videoInfoResponse = await fetch(`http://localhost:8000/api/preview/${data.session_id}`);
        console.log('Video info response status:', videoInfoResponse.status);
        
        if (videoInfoResponse.ok) {
            const previewData = await videoInfoResponse.json();  // Get video metadata
            console.log('Video info response data:', previewData);
            currentVideoInfo = previewData.video_info;  // Store video information
            displayVideoInfo();  // Update the UI with video details
            showAnalysisSection();  // Show the analysis settings section
        } else {
            const errorText = await videoInfoResponse.text();
            console.error('Failed to get video info:', videoInfoResponse.status, 'Error:', errorText);
        }

        hideUploadStatus();  // Hide upload progress indicator
    } catch (error) {
        console.error('Upload error:', error);  // Log any errors
        alert('Upload failed. Please try again.');  // Show error message to user
        hideUploadStatus();  // Hide upload progress indicator
    }
}

// Show the upload status indicator
function showUploadStatus() {
    uploadStatus.classList.remove('hidden');  // Make the upload status visible
}

// Hide the upload status indicator
function hideUploadStatus() {
    uploadStatus.classList.add('hidden');  // Hide the upload status
}

// Display video information in the UI
function displayVideoInfo() {
    console.log('Displaying video info:', currentVideoInfo);  // Log video information
    if (!currentVideoInfo) return;  // Exit if no video info available

    // Update all the video information displays
    document.getElementById('videoName').textContent = currentVideoInfo.filename;
    document.getElementById('videoDuration').textContent = formatTime(currentVideoInfo.duration);
    document.getElementById('videoResolution').textContent = currentVideoInfo.resolution;
    document.getElementById('videoFps').textContent = `${currentVideoInfo.frame_rate.toFixed(1)} fps`;
    document.getElementById('videoSize').textContent = `${(currentVideoInfo.file_size / (1024 * 1024)).toFixed(1)} MB`;
    document.getElementById('totalDuration').textContent = formatTime(currentVideoInfo.duration);
}

// Show the analysis settings section
function showAnalysisSection() {
    console.log('Showing analysis section');  // Log section display
    analysisSection.classList.remove('hidden');  // Make the section visible
}

// Show the timeline section with results
function showTimelineSection() {
    console.log('Showing timeline section');  // Log section display
    timelineSection.classList.remove('hidden');  // Make the section visible
}

// Convert seconds to a readable time format (MM:SS)
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);  // Calculate minutes
    const secs = Math.floor(seconds % 60);  // Calculate remaining seconds
    return `${mins}:${secs.toString().padStart(2, '0')}`;  // Format as MM:SS
}

// Analyze the uploaded video to detect scene changes
async function analyzeVideo() {
    if (!currentSessionId) {
        console.error('No session ID available');  // Log error if no session
        return;
    }

    showLoading('Analyzing Video', 'Detecting scene changes and cut points...');  // Show loading overlay
    
    try {
        // Get the current analysis settings from the UI
        const sensitivity = document.getElementById('sensitivitySlider').value;
        const ignoreCursor = document.getElementById('ignoreCursor').checked;
        const minSegmentDuration = document.getElementById('durationSlider').value;

        console.log('Analyzing with settings:', { sensitivity, ignoreCursor, minSegmentDuration });  // Log settings

        // Prepare the analysis request
        const requestBody = {
            session_id: currentSessionId,
            sensitivity: parseFloat(sensitivity),  // Convert to number
            ignore_cursor: ignoreCursor,
            min_segment_duration: parseFloat(minSegmentDuration)  // Convert to number
        };

        console.log('Sending analysis request:', requestBody);  // Log the request

        // Send the analysis request to the backend
        const response = await fetch('http://localhost:8000/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',  // Tell server we're sending JSON
            },
            body: JSON.stringify(requestBody),  // Convert request to JSON string
        });

        console.log('Analysis response status:', response.status);  // Log response status
        console.log('Analysis response headers:', response.headers);  // Log response headers

        // Check if the analysis was successful
        if (!response.ok) {
            const errorText = await response.text();  // Get error message
            console.error('Analysis failed with status:', response.status, 'Error:', errorText);
            throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
        }

        // Parse the analysis results
        const data = await response.json();  // Convert response to JavaScript object
        console.log('Analysis response data:', data);
        
        // Check if cut points were detected
        if (data.cut_points && Array.isArray(data.cut_points)) {
            currentCutPoints = data.cut_points;  // Store the detected cut points
            console.log('Cut points received:', currentCutPoints.length);  // Log number of cut points
            displayCutPoints();  // Update the UI with cut points
            showTimelineSection();  // Show the results section
        } else {
            console.error('No cut points in response or invalid format:', data);
            alert('Analysis completed but no cut points were detected.');  // Show warning to user
        }
        
        hideLoading();  // Hide loading overlay
    } catch (error) {
        console.error('Analysis error:', error);  // Log any errors
        alert('Analysis failed. Please try again.');  // Show error message to user
        hideLoading();  // Hide loading overlay
    }
}

// Display the detected cut points in the UI
function displayCutPoints() {
    console.log('Displaying cut points:', currentCutPoints);  // Log cut points
    const cutPointsList = document.getElementById('cutPointsList');  // Get the container element
    const cutPointsCount = document.getElementById('cutPointsCount');  // Get the count display
    
    cutPointsCount.textContent = currentCutPoints.length;  // Update the count
    cutPointsList.innerHTML = '';  // Clear the existing list

    // Create a display element for each cut point
    currentCutPoints.forEach((point, index) => {
        const cutPointElement = document.createElement('div');  // Create new div element
        cutPointElement.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors';
        
        // Fill the element with cut point information
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
        
        cutPointsList.appendChild(cutPointElement);  // Add the element to the list
    });
}

// Process the video into segments based on detected cut points
async function processVideo() {
    if (!currentSessionId || currentCutPoints.length === 0) return;  // Check if we have what we need

    showLoading('Processing Video', 'Creating video segments and preparing download...');  // Show loading overlay
    
    try {
        // Send the processing request to the backend
        const processResponse = await fetch('http://localhost:8000/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                cut_points: currentCutPoints  // Send the cut points to use for segmentation
            }),
        });

        // Check if processing was successful
        if (!processResponse.ok) {
            throw new Error('Processing failed');
        }

        const processData = await processResponse.json();  // Get processing results
        console.log('Process response:', processData);
        
        // Get information about the created files
        const downloadResponse = await fetch(`http://localhost:8000/api/download/${currentSessionId}`);
        if (downloadResponse.ok) {
            const downloadData = await downloadResponse.json();  // Get download information
            console.log('Download response:', downloadData);
            displayDownloadInfo(downloadData);  // Show download information to user
        }

        hideLoading();  // Hide loading overlay
    } catch (error) {
        console.error('Processing error:', error);  // Log any errors
        alert('Processing failed. Please try again.');  // Show error message to user
        hideLoading();  // Hide loading overlay
    }
}

// Display information about the processed files
function displayDownloadInfo(downloadData) {
    document.getElementById('downloadLocation').textContent = `Location: ${downloadData.output_directory}`;  // Show file location
    
    const filesList = document.getElementById('filesList');  // Get the files list container
    filesList.innerHTML = '';  // Clear the existing list
    
    // Create a list item for each processed file
    downloadData.files.forEach(file => {
        const li = document.createElement('li');  // Create new list item
        li.className = 'flex justify-between';  // Style the list item
        li.innerHTML = `
            <span>${file.name}</span>
            <span>${(file.size / 1024).toFixed(1)} KB</span>
        `;
        filesList.appendChild(li);  // Add to the list
    });
    
    document.getElementById('downloadInfo').classList.remove('hidden');  // Show the download info section
}

// Show the loading overlay with custom title and message
function showLoading(title, message) {
    document.getElementById('loadingTitle').textContent = title;  // Set the title
    document.getElementById('loadingMessage').textContent = message;  // Set the message
    loadingOverlay.classList.add('show');  // Make the overlay visible
}

// Hide the loading overlay
function hideLoading() {
    loadingOverlay.classList.remove('show');  // Hide the overlay
} 