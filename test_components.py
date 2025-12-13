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
        from wanvidgen.config import Config
        print("✅ Config import successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from wanvidgen.pipeline import VideoPipeline
        print("✅ VideoPipeline import successful")
    except Exception as e:
        print(f"❌ VideoPipeline import failed: {e}")
        return False
    
    try:
        from wanvidgen.gui import create_gui_manager
        print("✅ GUI components import successful")
    except Exception as e:
        print(f"❌ GUI components import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration functionality"""
    print("\nTesting configuration...")
    
    try:
        from wanvidgen.config import Config
        config = Config()
        
        # Test default values
        assert config.output.fps == 30
        assert config.output.width == 1024
        print("✅ Default configuration values correct")
        
        # Test setting values
        config.output.fps = 60
        assert config.output.fps == 60
        print("✅ Configuration setter/getter works")
        
        # Test to_dict
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['output']['fps'] == 60
        print("✅ Configuration export works")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_pipeline():
    """Test generation pipeline functionality"""
    print("\nTesting generation pipeline...")
    
    try:
        from wanvidgen.pipeline import create_default_pipeline
        from wanvidgen.config import Config
        
        config = Config()
        pipeline = create_default_pipeline(config.output.__dict__)
        
        # Test run
        print("Testing pipeline run...")
        result = pipeline.run({"prompt": "test prompt"})
        
        assert result["status"] == "success"
        assert result["prompt"] == "test prompt"
        print("✅ Pipeline generation completes successfully")
            
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
        from wanvidgen.pipeline import create_default_pipeline
        from wanvidgen.gui import create_gui_manager
        
        config = Config()
        pipeline = create_default_pipeline(config.output.__dict__)
        
        print("✅ Config and pipeline created for GUI")
        
        # Test customtkinter import separately (might not be installed)
        try:
            import customtkinter
            print("✅ CustomTkinter available for GUI")
        except ImportError:
            print("⚠️  CustomTkinter not installed - GUI testing limited")
            print("   Install with: pip install customtkinter")
        
        # Create manager
        gui_manager = create_gui_manager(config, pipeline, None)
        assert gui_manager is not None
        print("✅ GUI Manager created successfully")
        
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