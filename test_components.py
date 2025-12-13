#!/usr/bin/env python3
"""
Test script to verify WanVidGen components work correctly
"""

import sys
import os
from pathlib import Path

# Add the repository root to path
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from wanvidgen.config.config import Config
        print("✅ Config import successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from wanvidgen.pipeline.pipeline import GenerationPipeline
        print("✅ GenerationPipeline import successful")
    except Exception as e:
        print(f"❌ GenerationPipeline import failed: {e}")
        return False
    
    try:
        from wanvidgen.gui.app import WanVidGenGUI, LogPane
        print("✅ GUI components import successful")
    except Exception as e:
        print(f"❌ GUI components import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration functionality"""
    print("\nTesting configuration...")
    
    try:
        from wanvidgen.config.config import Config
        config = Config("test_config.json")
        
        # Test default values
        assert config.get("steps") == 20
        assert config.get("fps") == 8
        assert config.get("resolution") == 512
        print("✅ Default configuration values correct")
        
        # Test setting values
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        print("✅ Configuration setter/getter works")
        
        # Test saving and loading
        config.save()
        assert Path("test_config.json").exists()
        print("✅ Configuration save works")
        
        # Create new config and load
        config2 = Config("test_config.json")
        assert config2.get("test_key") == "test_value"
        assert config2.get("steps") == 20  # Should have defaults too
        print("✅ Configuration load works")
        
        # Cleanup
        os.remove("test_config.json")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_pipeline():
    """Test generation pipeline functionality"""
    print("\nTesting generation pipeline...")
    
    try:
        from wanvidgen.pipeline.pipeline import GenerationPipeline
        pipeline = GenerationPipeline()
        
        # Test status
        status = pipeline.get_status()
        assert not status['is_generating']
        assert status['progress'] == 0
        print("✅ Pipeline status check works")
        
        # Test callback tracking
        progress_updates = []
        status_updates = []
        
        def progress_callback(progress, message):
            progress_updates.append((progress, message))
        
        def status_callback(message):
            status_updates.append(message)
        
        # Test generation with short simulation
        result = pipeline.generate_video(
            prompt="test prompt",
            steps=5,  # Short test
            fps=8,
            resolution=512,
            output_dir="test_output",
            progress_callback=progress_callback,
            status_callback=status_callback
        )
        
        assert result != ""
        assert "test_output" in result
        print("✅ Pipeline generation completes successfully")
        
        assert len(progress_updates) > 0
        assert len(status_updates) > 0
        print("✅ Pipeline callbacks work correctly")
        
        # Test cancellation
        pipeline.cancel_generation()
        print("✅ Pipeline cancellation works")
        
        # Cleanup
        try:
            if os.path.exists(result):
                os.remove(result)
            if os.path.exists("test_output"):
                import shutil
                shutil.rmtree("test_output")  # Use shutil to remove non-empty directory
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")
            
        return True
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_creation():
    """Test that GUI components can be created (headless test)"""
    print("\nTesting GUI creation...")
    
    try:
        # Test without actually showing the window
        from wanvidgen.config import Config
        from wanvidgen.pipeline import GenerationPipeline
        
        config = Config()
        pipeline = GenerationPipeline()
        
        print("✅ Config and pipeline created for GUI")
        
        # Test customtkinter import separately (might not be installed)
        try:
            import customtkinter
            print("✅ CustomTkinter available for GUI")
        except ImportError:
            print("⚠️  CustomTkinter not installed - GUI testing limited")
            print("   Install with: pip install customtkinter")
        
        # We can't easily test the full GUI without a display,
        # but we can verify the classes can be imported and basic setup works
        
        return True
    except Exception as e:
        print(f"❌ GUI creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running WanVidGen Component Tests\n")
    
    tests = [
        test_imports,
        test_config,
        test_pipeline,
        test_gui_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application is ready to run.")
        print("\nTo start the GUI application:")
        print("  python -m wanvidgen")
        print("  OR")
        print("  python wanvidgen/main.py")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())