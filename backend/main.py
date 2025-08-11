# This is the main entry point for the Video Scene Detector backend server
# It sets up the web server and connects all the different parts of the application

# Import the necessary libraries for creating a web server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import our custom modules that handle different parts of the application
from app.api.routes import router as api_router  # This handles all the web requests (upload, analyze, etc.)
from app.core.config import settings  # This contains all the configuration settings

# Create the main web application
# FastAPI is a modern Python web framework that makes it easy to build APIs
app = FastAPI(
    title="Video Scene Detector API",  # The name that appears in the API documentation
    description="API for automatic video scene detection and segmentation",  # Description of what the API does
    version="1.0.0"  # Version number of the application
)

# CORS (Cross-Origin Resource Sharing) middleware
# This allows the frontend (running in a web browser) to communicate with this backend server
# Without this, the browser would block requests for security reasons
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any website (for testing purposes)
    allow_credentials=True,  # Allow cookies and authentication
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all types of headers
)

# Include the API routes (endpoints) that handle different requests
# The prefix "/api" means all routes will start with /api (e.g., /api/upload, /api/analyze)
app.include_router(api_router, prefix="/api")

# Create necessary directories if they don't exist
# These folders store uploaded videos, processed results, and temporary files
os.makedirs("uploads", exist_ok=True)  # Folder for uploaded video files
os.makedirs("processed", exist_ok=True)  # Folder for processed video segments
os.makedirs("temp", exist_ok=True)  # Folder for temporary files during processing

# Mount the processed folder as a static file server
# This allows the frontend to download processed video files directly
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Define a simple root endpoint that returns basic information
@app.get("/")
async def root():
    """Return a simple message when someone visits the root URL"""
    return {"message": "Video Scene Detector API"}

# Define a health check endpoint
# This is used to check if the server is running properly
@app.get("/health")
async def health_check():
    """Return the health status of the server"""
    return {"status": "healthy"}

# This block only runs if this file is executed directly (not imported)
if __name__ == "__main__":
    import uvicorn  # Uvicorn is the web server that runs our FastAPI application
    
    # Start the web server
    # host="0.0.0.0" means the server will accept connections from any IP address
    # port=8000 is the port number where the server will listen
    uvicorn.run(app, host="0.0.0.0", port=8000) 