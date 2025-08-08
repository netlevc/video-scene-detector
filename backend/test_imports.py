#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        from app.core.config import settings
        print("✅ Settings imported successfully")
    except Exception as e:
        print(f"❌ Error importing settings: {e}")
        return False
    
    try:
        from app.models.video import VideoInfo, CutPoint, ChangeType, VideoSession
        print("✅ Video models imported successfully")
    except Exception as e:
        print(f"❌ Error importing video models: {e}")
        return False
    
    try:
        from app.services.video_processor import VideoProcessor
        print("✅ VideoProcessor imported successfully")
    except Exception as e:
        print(f"❌ Error importing VideoProcessor: {e}")
        return False
    
    try:
        from app.api.routes import router
        print("✅ API routes imported successfully")
    except Exception as e:
        print(f"❌ Error importing API routes: {e}")
        return False
    
    return True

def test_pyscenedetect():
    """Test PySceneDetect imports"""
    print("\nTesting PySceneDetect...")
    
    try:
        from scenedetect import SceneManager, ContentDetector
        from scenedetect.stats_manager import StatsManager
        from scenedetect.video_manager import VideoManager
        print("✅ PySceneDetect modules imported successfully")
        
        # Test basic functionality
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        content_detector = ContentDetector(threshold=15)
        scene_manager.add_detector(content_detector)
        print("✅ PySceneDetect basic setup successful")
        
    except Exception as e:
        print(f"❌ Error with PySceneDetect: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🧪 Testing Video Scene Detector Imports")
    print("=" * 50)
    
    if test_imports() and test_pyscenedetect():
        print("\n✅ All imports successful!")
        print("🚀 Ready to start the server!")
        return True
    else:
        print("\n❌ Some imports failed!")
        return False

if __name__ == "__main__":
    main() 