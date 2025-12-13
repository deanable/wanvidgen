"""
Pipeline management for WanVidGen.

Handles the video generation process, coordinating model inference
and processing steps.
"""

from typing import Dict, Any, Optional, List
import logging
import time

logger = logging.getLogger(__name__)


class VideoPipeline:
    """Video generation pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.steps = []
        self.model_manager = None
        
    def set_model_manager(self, model_manager):
        """Set the model manager for the pipeline."""
        self.model_manager = model_manager
        
    def add_step(self, step):
        """Add a pipeline step (placeholder)."""
        self.steps.append(step)
        
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the video generation pipeline."""
        logger.info("Running video generation pipeline")
        
        prompt = input_data.get("prompt", "")
        if not prompt:
            return {"error": "No prompt provided"}
            
        if not self.model_manager:
            return {"error": "Model manager not initialized"}
            
        start_time = time.time()
        
        # Extract generation parameters
        width = input_data.get("width", self.config.get("width", 1024))
        height = input_data.get("height", self.config.get("height", 576))
        fps = input_data.get("fps", self.config.get("fps", 30))
        duration = input_data.get("duration", self.config.get("duration", 5))
        callback = input_data.get("callback", None)
        
        # Call model to generate frames
        try:
            generation_result = self.model_manager.generate(
                prompt=prompt,
                width=width,
                height=height,
                fps=fps,
                duration=duration,
                callback=callback
            )
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
            
        result = {
            "status": "success",
            "prompt": prompt,
            "pipeline": "WanVidGen-Pipeline",
            "generation_time": time.time() - start_time,
            **generation_result # Includes 'frames', 'video_path' etc.
        }
        
        return result


def create_default_pipeline(config: Dict[str, Any], model_manager=None) -> VideoPipeline:
    """Create default video generation pipeline."""
    pipeline = VideoPipeline(config)
    if model_manager:
        pipeline.set_model_manager(model_manager)
    return pipeline
