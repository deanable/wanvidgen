#!/usr/bin/env python3
"""Smoke test to verify pipeline instantiation and basic functionality."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from wanvidgen.exceptions import (
            WanVidGenException,
            ModelLoadError,
            ConfigError,
            GPUMemoryError,
            PipelineError,
            GenerationError,
        )
        print("  ✓ Exceptions imported successfully")
        
        from wanvidgen.memory import MemoryManager
        print("  ✓ MemoryManager imported successfully")
        
        from wanvidgen.models import CLIPManager, VAEManager, UNetManager
        print("  ✓ Model managers imported successfully")
        
        from wanvidgen.pipeline import GenerationPipeline, GenerationConfig, GenerationResult
        print("  ✓ Pipeline imported successfully")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_pipeline_instantiation():
    """Test basic pipeline instantiation."""
    print("\nTesting pipeline instantiation...")
    
    try:
        from wanvidgen.pipeline import GenerationPipeline
        from wanvidgen.exceptions import ConfigError
        
        # Try to create with non-existent paths (should fail with ConfigError)
        try:
            pipeline = GenerationPipeline(
                clip_config_path="/nonexistent/clip.gguf",
                vae_config_path="/nonexistent/vae.gguf",
                unet_config_path="/nonexistent/unet.gguf",
            )
            print("  ✗ Should have raised ConfigError for missing models")
            return False
        except ConfigError as e:
            print(f"  ✓ ConfigError raised as expected: {e.user_message}")
        
        # Try with temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            clip_path = tmpdir / "clip.gguf"
            vae_path = tmpdir / "vae.gguf"
            unet_path = tmpdir / "unet.gguf"
            
            clip_path.touch()
            vae_path.touch()
            unet_path.touch()
            
            pipeline = GenerationPipeline(
                clip_config_path=clip_path,
                vae_config_path=vae_path,
                unet_config_path=unet_path,
                device="cpu",
            )
            
            print(f"  ✓ Pipeline instantiated successfully")
            print(f"    - Device: {pipeline.device}")
            print(f"    - Models loaded: {pipeline.is_loaded()}")
            
            # Test loading models
            pipeline.load()
            print(f"  ✓ Models loaded")
            print(f"    - Models loaded: {pipeline.is_loaded()}")
            
            # Test unloading
            pipeline.unload()
            print(f"  ✓ Models unloaded")
            print(f"    - Models loaded: {pipeline.is_loaded()}")
        
        return True
    except Exception as e:
        print(f"  ✗ Pipeline instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generation_config():
    """Test GenerationConfig."""
    print("\nTesting GenerationConfig...")
    
    try:
        from wanvidgen.pipeline import GenerationConfig
        
        # Test basic config
        config = GenerationConfig(prompt="Test prompt")
        print(f"  ✓ Basic config created")
        print(f"    - Prompt: {config.prompt}")
        print(f"    - Height: {config.height}")
        print(f"    - Width: {config.width}")
        print(f"    - FPS: {config.fps}")
        
        # Test custom config
        config = GenerationConfig(
            prompt="Custom prompt",
            negative_prompt="bad quality",
            height=768,
            width=768,
            num_inference_steps=75,
            fps=16,
            seed=123,
            clip_guidance_scale=10.0,
        )
        print(f"  ✓ Custom config created")
        print(f"    - Prompt: {config.prompt}")
        print(f"    - Negative prompt: {config.negative_prompt}")
        print(f"    - Height: {config.height}")
        print(f"    - Steps: {config.num_inference_steps}")
        print(f"    - Seed: {config.seed}")
        
        # Test to_dict
        config_dict = config.to_dict()
        print(f"  ✓ Config to_dict() works")
        print(f"    - Keys: {list(config_dict.keys())}")
        
        return True
    except Exception as e:
        print(f"  ✗ GenerationConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exception_hierarchy():
    """Test exception hierarchy."""
    print("\nTesting exception hierarchy...")
    
    try:
        from wanvidgen.exceptions import (
            WanVidGenException,
            ModelLoadError,
            ConfigError,
            GPUMemoryError,
            PipelineError,
            GenerationError,
        )
        
        exceptions = [
            ("ModelLoadError", ModelLoadError),
            ("ConfigError", ConfigError),
            ("GPUMemoryError", GPUMemoryError),
            ("PipelineError", PipelineError),
            ("GenerationError", GenerationError),
        ]
        
        for name, exc_class in exceptions:
            exc = exc_class("Test message", user_message="User friendly message")
            assert isinstance(exc, WanVidGenException)
            assert exc.message == "Test message"
            assert exc.user_message == "User friendly message"
            print(f"  ✓ {name}")
        
        return True
    except Exception as e:
        print(f"  ✗ Exception hierarchy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_manager():
    """Test MemoryManager."""
    print("\nTesting MemoryManager...")
    
    try:
        from wanvidgen.memory import MemoryManager
        
        # Test on CPU
        manager = MemoryManager(device="cpu")
        print(f"  ✓ MemoryManager created for CPU")
        print(f"    - Device: {manager.device}")
        print(f"    - is_cuda: {manager.is_cuda}")
        
        # Test memory checks
        free_mb = manager.get_free_gpu_memory_mb()
        print(f"  ✓ get_free_gpu_memory_mb() returned: {free_mb}")
        
        # Test availability check
        available = manager.check_available_memory(1000)
        print(f"  ✓ check_available_memory(1000): {available}")
        
        # Test memory stats
        stats = manager.get_memory_stats()
        print(f"  ✓ get_memory_stats() returned: {stats}")
        
        # Test free memory (should not raise)
        manager.free_memory()
        print(f"  ✓ free_memory() executed")
        
        return True
    except Exception as e:
        print(f"  ✗ MemoryManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("WanVidGen Pipeline Smoke Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Exception Hierarchy", test_exception_hierarchy()))
    results.append(("MemoryManager", test_memory_manager()))
    results.append(("GenerationConfig", test_generation_config()))
    results.append(("Pipeline Instantiation", test_pipeline_instantiation()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All smoke tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
