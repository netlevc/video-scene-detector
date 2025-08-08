#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from scenedetect import SceneManager, ContentDetector
    from scenedetect.stats_manager import StatsManager
    from scenedetect.video_manager import VideoManager
    
    print("✅ PySceneDetect imports successful")
    
    # Test the API
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    content_detector = ContentDetector(threshold=27)
    scene_manager.add_detector(content_detector)
    
    print("✅ SceneManager and ContentDetector created successfully")
    
    # Check available methods
    print(f"SceneManager methods: {[method for method in dir(scene_manager) if not method.startswith('_')]}")
    print(f"VideoManager methods: {[method for method in dir(VideoManager) if not method.startswith('_')]}")
    
    # Test with a dummy video path (won't actually process)
    try:
        video_manager = VideoManager(['dummy.mp4'])
        print("✅ VideoManager created successfully")
        
        # Try different API calls
        print("\nTesting different API calls:")
        
        # Method 1: Direct call
        try:
            scene_manager.detect_scenes()
            print("✅ Method 1: scene_manager.detect_scenes() - works")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: With video_manager parameter
        try:
            scene_manager.detect_scenes(video_manager=video_manager)
            print("✅ Method 2: scene_manager.detect_scenes(video_manager=video_manager) - works")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: Set video manager first
        try:
            scene_manager.set_video_manager(video_manager)
            scene_manager.detect_scenes()
            print("✅ Method 3: set_video_manager() then detect_scenes() - works")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            
    except Exception as e:
        print(f"❌ VideoManager creation failed: {e}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}") 