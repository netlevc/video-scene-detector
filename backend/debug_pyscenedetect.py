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
    
    # Test with a real video file if available
    test_video = None
    for root, dirs, files in os.walk("uploads"):
        for file in files:
            if file.endswith(('.mp4', '.avi', '.mov')):
                test_video = os.path.join(root, file)
                break
        if test_video:
            break
    
    if not test_video:
        print("❌ No test video found in uploads directory")
        sys.exit(1)
    
    print(f"✅ Found test video: {test_video}")
    
    # Test the API with real video
    try:
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        content_detector = ContentDetector(threshold=27)
        scene_manager.add_detector(content_detector)
        
        print("✅ SceneManager and ContentDetector created successfully")
        
        # Test with real video
        video_manager = VideoManager([test_video])
        print("✅ VideoManager created successfully")
        
        # Try the API call that's failing
        try:
            scene_manager.set_video_manager(video_manager)
            print("✅ set_video_manager() successful")
            
            scene_manager.detect_scenes()
            print("✅ detect_scenes() successful")
            
            scene_list = scene_manager.get_scene_list()
            print(f"✅ Found {len(scene_list)} scenes")
            
            for i, scene in enumerate(scene_list):
                start_frame = scene[0].get_frames()
                start_time = scene[0].get_seconds()
                print(f"  Scene {i+1}: Frame {start_frame}, Time {start_time:.2f}s")
                
        except Exception as e:
            print(f"❌ Error during scene detection: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error creating managers: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 