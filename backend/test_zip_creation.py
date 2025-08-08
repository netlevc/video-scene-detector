#!/usr/bin/env python3

import zipfile
import os
from pathlib import Path

def test_zip_creation():
    """Test zip file creation to debug the corruption issue"""
    
    # Create a test directory
    test_dir = Path("test_zip")
    test_dir.mkdir(exist_ok=True)
    
    # Create some test files
    test_files = [
        ("test1.txt", "This is test file 1"),
        ("test2.txt", "This is test file 2"),
        ("subfolder/test3.txt", "This is test file 3 in subfolder")
    ]
    
    # Create the test files
    for file_path, content in test_files:
        full_path = test_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    # Create zip file
    zip_path = Path("test_output.zip")
    
    try:
        print(f"Creating zip file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in test_dir.rglob("*"):
                if file_path.is_file():
                    # Use relative path within the zip
                    arcname = file_path.relative_to(test_dir)
                    print(f"Adding to zip: {file_path} -> {arcname}")
                    zipf.write(file_path, arcname)
        
        # Verify the zip file
        if not zip_path.exists():
            print("❌ Zip file was not created")
            return False
        
        if zip_path.stat().st_size == 0:
            print("❌ Zip file is empty")
            return False
        
        print(f"✅ Zip file created successfully: {zip_path}")
        print(f"✅ File size: {zip_path.stat().st_size} bytes")
        
        # Test reading the zip file
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            print(f"✅ Zip contains {len(file_list)} files:")
            for file in file_list:
                print(f"  - {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating zip file: {e}")
        return False

if __name__ == "__main__":
    success = test_zip_creation()
    if success:
        print("\n🎉 Zip creation test passed!")
    else:
        print("\n❌ Zip creation test failed!") 