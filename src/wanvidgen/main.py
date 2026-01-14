"""
Main entry point for WanVidGen application.

Handles command-line interface, configuration loading,
and application initialization.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Allow running directly by setting up package context
if __name__ == "__main__" and __package__ is None:
    file = Path(__file__).resolve()
    sys.path.insert(0, str(file.parents[1]))
    __package__ = "wanvidgen"

from .config import Config, load_config
from .utils import get_system_info, check_dependencies, ensure_model_availability
from .log_config import configure_logging, LogConfig
from .gui import create_gui_manager
from .pipeline import create_default_pipeline
from .output.handlers import save_generation
from .models import create_model_manager


logger = logging.getLogger(__name__)


def setup_arg_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="WanVidGen - Video Generation with GGUF Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --gui                          # Start GUI application
  %(prog)s --generate "A cat playing piano"  # Generate video from prompt
  %(prog)s --check-system                # Check system compatibility
        """
    )
    
    # Main operation modes
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument("--gui", action="store_true",
                          help="Start the graphical user interface")
    mode_group.add_argument("--generate", type=str,
                          help="Generate video from prompt text")
    mode_group.add_argument("--check-system", action="store_true",
                          help="Check system compatibility and exit")
    
    # Configuration options
    parser.add_argument("--env-file", type=str,
                      help="Path to environment file (.env)")
    
    # Model options
    parser.add_argument("--model-path", type=str,
                      help="Path to model file")
    parser.add_argument("--model-name", type=str,
                      help="Model name identifier")
    parser.add_argument("--device", type=str, choices=["auto", "cpu", "cuda", "mps"],
                      default="auto", help="Computation device")
    parser.add_argument("--precision", type=str, choices=["Q5", "Q6", "FP16", "FP32"],
                      default="Q5", help="Model precision")
    
    # Output options
    parser.add_argument("--output-dir", type=str, default="./outputs",
                      help="Output directory for generated videos")
    
    # Video options
    parser.add_argument("--width", type=int, default=1024,
                      help="Video width")
    parser.add_argument("--height", type=int, default=576,
                      help="Video height")
    parser.add_argument("--fps", type=int, default=30,
                      help="Frames per second")
    parser.add_argument("--quality", type=str, choices=["low", "medium", "high", "ultra"],
                      default="high", help="Video quality")
    
    # Logging options
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                      default="INFO", help="Logging level")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug mode")
    
    return parser


def check_system_compatibility() -> bool:
    """Check system compatibility and print results."""
    print("=== System Compatibility Check ===\n")
    
    # Get system info
    system_info = get_system_info()
    print("System Information:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    print("\nDependency Check:")
    dependencies = check_dependencies()
    
    all_good = True
    for package, available in dependencies.items():
        status = "✓" if available else "✗"
        print(f"  {package}: {status}")
        if not available:
            all_good = False
    
    if all_good:
        print("\n✓ All dependencies available (placeholder)")
    else:
        print("\n✗ Some dependencies missing. Please install required packages.")
    
    return all_good


def generate_video(prompt: str, config: Config, output_name: Optional[str] = None) -> bool:
    """Generate video from prompt."""
    try:
        print(f"=== Video Generation ===\n")
        print(f"Prompt: {prompt}")
        print(f"Configuration:")
        print(f"  Model: {config.model.model_name or config.model.model_path or 'placeholder'}")
        print(f"  Device: {config.model.device}")
        print(f"  Precision: {config.model.precision}")
        print(f"  Output: {config.output.output_dir}")
        print(f"  Resolution: {config.output.width}x{config.output.height}")
        print(f"  FPS: {config.output.fps}")
        print()

        # Create components
        model_manager = create_model_manager(config.model.__dict__)
        pipeline = create_default_pipeline(config.output.__dict__, model_manager)
        
        # Load model
        print("Loading model...")
        if not model_manager.load_model():
            print("✗ Failed to load model")
            return False
        print("✓ Model loaded")
        
        # Run pipeline
        print("Generating video...")
        import time
        start_time = time.time()
        
        input_data = {"prompt": prompt}
        result = pipeline.run(input_data)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Save output
        if result and result.get("status") == "success":
            metadata = {
                "prompt": prompt,
                "generation_time": generation_time,
                "config": config.to_dict(),
                "result": result,
            }
            
            # Save video if frames are present
            if "frames" in result:
                saved_files = save_generation(
                    frames=result["frames"],
                    metadata=metadata,
                    output_dir=Path(config.output.output_dir) / f"gen_{int(time.time())}",
                    fps=config.output.fps
                )
                print(f"✓ Video saved to: {saved_files.get('mp4', saved_files.get('png'))}")
                print(f"✓ Generation completed in {generation_time:.2f} seconds")
        
        # Cleanup
        model_manager.unload_model()
        
        return True
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        print(f"✗ Generation failed: {e}")
        return False


def start_gui(config: Config) -> bool:
    """Start the GUI application."""
    try:
        print("Starting GUI application...")
        
        # Create components
        model_manager = create_model_manager(config.model.__dict__)
        pipeline = create_default_pipeline(config.output.__dict__, model_manager)

        # Create and start GUI
        gui_manager = create_gui_manager(config, pipeline)
        if gui_manager is None:
            print("✗ GUI not available")
            return False
        
        return gui_manager.start()
        
    except Exception as e:
        logger.error(f"GUI failed to start: {e}")
        print(f"✗ GUI failed to start: {e}")
        return False


def update_config_from_args(config: Config, args: argparse.Namespace) -> Config:
    """Update configuration from command line arguments."""
    # Update model configuration
    if args.model_path:
        config.model.model_path = args.model_path
    if args.model_name:
        config.model.model_name = args.model_name
    if args.device:
        config.model.device = args.device
    if args.precision:
        config.model.precision = args.precision
    
    # Update output configuration
    if args.output_dir:
        config.output.output_dir = args.output_dir
    if args.width:
        config.output.width = args.width
    if args.height:
        config.output.height = args.height
    if args.fps:
        config.output.fps = args.fps
    if args.quality:
        config.output.quality = args.quality
    
    # Update logging configuration
    if args.log_level:
        config.logging.level = args.log_level
    if args.debug:
        config.debug = True
        config.logging.level = "DEBUG"
    
    # Update environment file
    if args.env_file:
        config.env_file = args.env_file
    
    return config


def main() -> int:
    """Main entry point."""
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.env_file)
        config = update_config_from_args(config, args)
        
        # Setup logging
        log_config = LogConfig(
            log_level=config.logging.level,
            console_output=config.logging.console_logging,
            file_output=config.logging.file_logging,
        )
        configure_logging(log_config)
        
        logger.info("WanVidGen starting...")
        logger.info(f"Version: 0.1.0")
        logger.info(f"Python version: {sys.version}")
        
        # Check for model availability on startup
        if not args.check_system:  # Don't download if just checking system
            if not ensure_model_availability(config):
                logger.warning("Model check failed or model not found. Some features may not work.")

        # Handle different operation modes
        success = True
        if args.check_system:
            success = check_system_compatibility()
        elif args.generate:
            success = generate_video(args.generate, config, None)
        elif args.gui:
            success = start_gui(config)
        else:
            # If no mode specified, show help
            parser.print_help()
            return 0
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"✗ Application error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1