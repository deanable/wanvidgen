"""Basic example of using the GenerationPipeline."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.pipeline import GenerationPipeline, GenerationConfig


def main():
    """Example of basic pipeline usage."""
    # Note: This example assumes model weights are available at these paths.
    # For testing without real models, use the test suite instead.
    
    clip_model_path = Path("./models/clip.gguf")
    vae_model_path = Path("./models/vae.gguf")
    unet_model_path = Path("./models/unet.gguf")

    try:
        # Initialize pipeline
        pipeline = GenerationPipeline(
            clip_config_path=clip_model_path,
            vae_config_path=vae_model_path,
            unet_config_path=unet_model_path,
            device="cuda",
            clip_quantization="q5",
            vae_quantization="q5",
            unet_quantization="q6",
        )

        # Use context manager for automatic model loading/unloading
        with pipeline:
            # Configure generation
            config = GenerationConfig(
                prompt="A beautiful landscape at sunset",
                negative_prompt="blurry, low quality",
                height=512,
                width=512,
                num_inference_steps=50,
                sampler="ddim",
                scheduler="linear",
                seed=42,
                fps=8,
                clip_guidance_scale=7.5,
            )

            # Generate video
            result = pipeline.generate(config)

            print(f"Generated {result.get_frame_count()} frames")
            print(f"Frame dimensions: {result.metadata['height']}x{result.metadata['width']}")
            print(f"FPS: {result.get_fps()}")
            print(f"Generation completed successfully!")

    except FileNotFoundError:
        print(f"Model files not found. Expected paths:")
        print(f"  - {clip_model_path}")
        print(f"  - {vae_model_path}")
        print(f"  - {unet_model_path}")
        print(f"\nFor testing without models, use the test suite.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
