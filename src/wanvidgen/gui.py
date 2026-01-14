"""
GUI module for WanVidGen using CustomTkinter.

Placeholder module for graphical user interface.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

try:
    import customtkinter as ctk
    from tkinter import messagebox
    from PIL import Image
    CTK_AVAILABLE = True
except ImportError:
    logger.warning("CustomTkinter not available. GUI will be disabled.")
    CTK_AVAILABLE = False
    ctk: Any = None
    messagebox: Any = None
    Image: Any = None


class WanVidGenApp:
    """Main GUI Application class for WanVidGen."""
    
    def __init__(self, config, pipeline, output_manager):
        if not CTK_AVAILABLE:
            raise ImportError("CustomTkinter not available")
        
        self.config = config
        self.pipeline = pipeline
        self.output_manager = output_manager
        self.is_generating = False
        
        # Setup Window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("WanVidGen - AI Video Generator")
        self.root.geometry("1100x700")
        
        # Grid configuration
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components."""
        # Sidebar for settings
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="WanVidGen", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Settings Area
        self.setup_settings_area()
        
        # Main Content Area
        self.main_area = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1) # Log area expands
        
        # Tab View for Preview/Log
        self.tab_view = ctk.CTkTabview(self.main_area)
        self.tab_view.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.tab_view.add("Preview")
        self.tab_view.add("Log")
        
        # Preview Tab
        self.preview_label = ctk.CTkLabel(self.tab_view.tab("Preview"), text="No generation yet")
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Log Tab
        self.log_text = ctk.CTkTextbox(self.tab_view.tab("Log"), height=300, state="disabled")
        self.log_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Prompt Input
        self.prompt_text = ctk.CTkTextbox(self.main_area, height=80)
        self.prompt_text.grid(row=6, column=0, sticky="ew", pady=(10, 10))
        self.prompt_text.insert("1.0", "A cinematic shot of a robot painting a canvas in a futuristic studio...")
        
        # Generate Button
        self.generate_btn = ctk.CTkButton(self.main_area, text="Generate Video", command=self.start_generation, height=40)
        self.generate_btn.grid(row=7, column=0, sticky="ew", pady=(0, 20))
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.main_area)
        self.progress_bar.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        self.progress_bar.set(0)
        
    def setup_settings_area(self):
        """Setup settings controls in sidebar."""
        # Resolution
        self.res_label = ctk.CTkLabel(self.sidebar, text="Resolution", anchor="w")
        self.res_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.width_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Width")
        self.width_entry.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.width_entry.insert(0, str(self.config.output.width))
        
        self.height_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Height")
        self.height_entry.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.height_entry.insert(0, str(self.config.output.height))
        
        # Duration
        self.dur_label = ctk.CTkLabel(self.sidebar, text="Duration (s)", anchor="w")
        self.dur_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.dur_slider = ctk.CTkSlider(self.sidebar, from_=1, to=10, number_of_steps=9)
        self.dur_slider.grid(row=5, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.dur_slider.set(self.config.output.duration)
        
        # FPS
        self.fps_label = ctk.CTkLabel(self.sidebar, text="FPS", anchor="w")
        self.fps_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.fps_slider = ctk.CTkSlider(self.sidebar, from_=10, to=60, number_of_steps=50)
        self.fps_slider.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.fps_slider.set(self.config.output.fps)
        
        # Model Info
        self.model_label = ctk.CTkLabel(self.sidebar, text="Model Settings", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.model_label.grid(row=8, column=0, padx=20, pady=(20, 0), sticky="w")
        
        device_txt = f"Device: {self.config.model.device}"
        self.device_label = ctk.CTkLabel(self.sidebar, text=device_txt, anchor="w", text_color="gray")
        self.device_label.grid(row=9, column=0, padx=20, pady=(5, 0), sticky="w")

    def log(self, message):
        """Add message to log window."""
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        logger.info(message)

    def start_generation(self):
        """Handler for generate button."""
        if self.is_generating:
            return
            
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt")
            return
            
        # Update config from UI
        try:
            self.config.output.width = int(self.width_entry.get())
            self.config.output.height = int(self.height_entry.get())
            self.config.output.fps = int(self.fps_slider.get())
            self.config.output.duration = int(self.dur_slider.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid settings values")
            return
            
        self.is_generating = True
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.progress_bar.start()
        
        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self._run_pipeline, args=(prompt,))
        thread.daemon = True
        thread.start()
        
    def _update_preview(self, frame, current_frame, total_frames):
        """Callback to update preview image."""
        try:
            # Convert numpy array to PIL Image
            image = Image.fromarray(frame)
            # Resize for preview (keep aspect ratio)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(400, 225))
            
            # Schedule UI update
            self.root.after(0, lambda: self._set_preview_image(ctk_image, current_frame, total_frames))
        except Exception as e:
            logger.error(f"Preview update failed: {e}")

    def _set_preview_image(self, ctk_image, current, total):
        """Update the label with the new image."""
        self.preview_label.configure(image=ctk_image, text="")
        self.progress_bar.set(current / total)

    def _run_pipeline(self, prompt):
        """Execute pipeline in background thread."""
        try:
            self.log(f"Starting generation for: {prompt[:30]}...")
            self.log(f"Settings: {self.config.output.width}x{self.config.output.height}, {self.config.output.duration}s @ {self.config.output.fps}fps")
            
            input_data = {
                "prompt": prompt,
                "width": self.config.output.width,
                "height": self.config.output.height,
                "fps": self.config.output.fps,
                "duration": self.config.output.duration,
                "num_frames": self.config.output.duration * self.config.output.fps,
                "callback": self._update_preview
            }
            
            # Run pipeline
            result = self.pipeline.run(input_data)
            
            if result.get("status") == "success":
                self.log("Generation completed successfully!")
                # Save output using handlers
                if "frames" in result:
                    from pathlib import Path
                    from .output.handlers import save_generation
                    output_dir = Path(self.config.output.output_dir) / f"gen_{int(time.time())}"
                    saved_files = save_generation(
                        frames=result["frames"],
                        metadata=result,
                        output_dir=output_dir,
                        fps=self.config.output.fps
                    )
                    self.log(f"Saved to {output_dir}")
            else:
                self.log(f"Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.log(f"Error during generation: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Schedule UI update on main thread
            self.root.after(0, self._generation_finished)
            
    def _generation_finished(self):
        """Reset UI after generation."""
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Generate Video")
        self.progress_bar.stop()
        self.progress_bar.set(1.0)
        messagebox.showinfo("Finished", "Video generation process finished.")
        
    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()
        

class SimpleGUIManager:
    """Simple GUI manager placeholder."""

    def __init__(self, config_manager=None, pipeline=None):
        self.config_manager = config_manager
        self.pipeline = pipeline
        self.app = None
        
    def start(self) -> bool:
        """Start the GUI application."""
        if not CTK_AVAILABLE:
            logger.error("CustomTkinter not available. Cannot start GUI.")
            return False
        
        try:
            self.app = WanVidGenApp(self.config_manager, self.pipeline, None)
            self.app.run()
            return True
        except Exception as e:
            logger.error(f"Failed to start GUI: {e}")
            return False


def create_gui_manager(config_manager=None, pipeline=None):
    """Create GUI manager instance."""
    return SimpleGUIManager(config_manager, pipeline)