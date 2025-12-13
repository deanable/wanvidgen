"""Basic example of using the VideoPipeline."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.pipeline import create_default_pipeline
from wanvidgen.config import Config


def main():
    """Example of basic pipeline usage."""
    
    # Initialize configuration
    config = Config()
    
    # Configure settings
    config.model.device = "cuda"
    config.model.precision = "Q5"
    
    config.output.width = 512
    config.output.height = 512
    config.output.fps = 8
    
    print("Initializing pipeline...")
    
    # Create pipeline
    pipeline = create_default_pipeline(config.output.__dict__)
    
    prompt = "A beautiful landscape at sunset"
    print(f"Generating video for prompt: '{prompt}'")
    
    # Run generation
    result = pipeline.run({"prompt": prompt})
    
    if result.get("status") == "success":
        print("Generation completed successfully!")
        print(f"Result: {result}")
    else:
        print(f"Generation failed: {result.get('error')}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
