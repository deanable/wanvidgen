"""
CustomTkinter GUI for WanVidGen application
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
from typing import Optional, Callable
import queue
import traceback
import sys
from pathlib import Path

# Add the repository root to path for imports
repo_root = str(Path(__file__).parent.parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from wanvidgen.pipeline import GenerationPipeline
from wanvidgen.config import Config


class LogPane:
    """Custom log pane with auto-scrolling and color coding"""
    
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.text_widget = scrolledtext.ScrolledText(
            self.frame,
            height=8,
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            font=("Consolas", 10)
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_widget.config(state="disabled")  # Read-only
        
    def clear(self):
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, "end")
        self.text_widget.config(state="disabled")
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with optional level"""
        self.text_widget.config(state="normal")
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Color coding
        if level == "ERROR":
            color = "#ff4444"
        elif level == "WARNING":
            color = "#ffaa00"
        elif level == "SUCCESS":
            color = "#44ff44"
        else:
            color = "#ffffff"
            
        # Insert text with color
        self.text_widget.insert("end", f"[{timestamp}] {level}: {message}\n")
        
        # Auto-scroll to bottom
        self.text_widget.see("end")
        self.text_widget.config(state="disabled")
        
    def log_progress(self, message: str):
        """Log a progress message"""
        self.log(message, "PROGRESS")
        
    def log_error(self, message: str):
        """Log an error message"""
        self.log(message, "ERROR")
        
    def log_success(self, message: str):
        """Log a success message"""
        self.log(message, "SUCCESS")


class WanVidGenGUI:
    """Main GUI application for WanVidGen"""
    
    def __init__(self):
        # Set up CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.config = Config()
        self.pipeline = GenerationPipeline(self.config.get_all())
        self.is_generating = False
        
        # Queue for thread-safe GUI updates
        self.log_queue = queue.Queue()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("WanVidGen - Video Generation GUI")
        self.root.geometry(f"{self.config.get('window_width', 1200)}x{self.config.get('window_height', 800)}")
        self.root.minsize(1000, 700)
        
        # Set up GUI
        self._setup_widgets()
        self._setup_menu()
        self._load_saved_config()
        
        # Start log processing
        self._process_log_queue()
        
    def _setup_widgets(self):
        """Set up the main GUI widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook-style tabs
        self.tab_view = ctk.CTkTabview(main_frame)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Generation tab
        self.generation_tab = self.tab_view.add("Generation")
        self._setup_generation_tab()
        
        # Settings tab  
        self.settings_tab = self.tab_view.add("Settings")
        self._setup_settings_tab()
        
        # Console/Log tab
        self.console_tab = self.tab_view.add("Console")
        self._setup_console_tab()
        
        # Status bar
        self._setup_status_bar()
        
    def _setup_generation_tab(self):
        """Set up the generation tab with form fields"""
        # Create scrollable frame for generation parameters
        scroll_frame = ctk.CTkScrollableFrame(self.generation_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Prompt section
        prompt_frame = ctk.CTkFrame(scroll_frame)
        prompt_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(prompt_frame, text="Generation Prompt", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.prompt_textbox = ctk.CTkTextbox(prompt_frame, height=80)
        self.prompt_textbox.pack(fill="x", padx=10, pady=(0,10))
        
        # Negative prompt section
        neg_frame = ctk.CTkFrame(scroll_frame)
        neg_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(neg_frame, text="Negative Prompt", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.negative_prompt_textbox = ctk.CTkTextbox(neg_frame, height=60)
        self.negative_prompt_textbox.pack(fill="x", padx=10, pady=(0,10))
        
        # Parameters section
        params_frame = ctk.CTkFrame(scroll_frame)
        params_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(params_frame, text="Generation Parameters", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        # Sampler and Scheduler row
        row1_frame = ctk.CTkFrame(params_frame)
        row1_frame.pack(fill="x", padx=10, pady=5)
        
        # Sampler dropdown
        ctk.CTkLabel(row1_frame, text="Sampler:").grid(row=0, column=0, sticky="w", padx=(10,5), pady=10)
        self.sampler_var = tk.StringVar(value=self.config.get("sampler"))
        self.sampler_menu = ctk.CTkOptionMenu(
            row1_frame, 
            variable=self.sampler_var,
            values=self.config.get("available_samplers", [])
        )
        self.sampler_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Scheduler dropdown
        ctk.CTkLabel(row1_frame, text="Scheduler:").grid(row=0, column=2, sticky="w", padx=(20,5), pady=10)
        self.scheduler_var = tk.StringVar(value=self.config.get("scheduler"))
        self.scheduler_menu = ctk.CTkOptionMenu(
            row1_frame,
            variable=self.scheduler_var,
            values=self.config.get("available_schedulers", [])
        )
        self.scheduler_menu.grid(row=0, column=3, sticky="ew", padx=5, pady=10)
        
        row1_frame.grid_columnconfigure(1, weight=1)
        row1_frame.grid_columnconfigure(3, weight=1)
        
        # Quantization and Steps row
        row2_frame = ctk.CTkFrame(params_frame)
        row2_frame.pack(fill="x", padx=10, pady=5)
        
        # Quantization dropdown
        ctk.CTkLabel(row2_frame, text="Quantization:").grid(row=0, column=0, sticky="w", padx=(10,5), pady=10)
        self.quantization_var = tk.StringVar(value=self.config.get("quantization"))
        self.quantization_menu = ctk.CTkOptionMenu(
            row2_frame,
            variable=self.quantization_var,
            values=self.config.get("available_quantizations", [])
        )
        self.quantization_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Steps slider
        ctk.CTkLabel(row2_frame, text="Steps:").grid(row=0, column=2, sticky="w", padx=(20,5), pady=10)
        self.steps_var = tk.IntVar(value=self.config.get("steps"))
        steps_frame = ctk.CTkFrame(row2_frame)
        steps_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=10)
        
        self.steps_slider = ctk.CTkSlider(steps_frame, from_=10, to=50, variable=self.steps_var, number_of_steps=40)
        self.steps_slider.pack(fill="x", padx=5, pady=(10,0))
        self.steps_label = ctk.CTkLabel(steps_frame, text=str(self.config.get("steps")))
        self.steps_label.pack(pady=(0,10))
        
        self.steps_slider.configure(command=self._on_steps_change)
        
        row2_frame.grid_columnconfigure(1, weight=1)
        row2_frame.grid_columnconfigure(3, weight=1)
        
        # FPS and Resolution row
        row3_frame = ctk.CTkFrame(params_frame)
        row3_frame.pack(fill="x", padx=10, pady=5)
        
        # FPS slider
        ctk.CTkLabel(row3_frame, text="FPS:").grid(row=0, column=0, sticky="w", padx=(10,5), pady=10)
        self.fps_var = tk.IntVar(value=self.config.get("fps"))
        fps_frame = ctk.CTkFrame(row3_frame)
        fps_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        self.fps_slider = ctk.CTkSlider(fps_frame, from_=4, to=24, variable=self.fps_var, number_of_steps=20)
        self.fps_slider.pack(fill="x", padx=5, pady=(10,0))
        self.fps_label = ctk.CTkLabel(fps_frame, text=str(self.config.get("fps")))
        self.fps_label.pack(pady=(0,10))
        
        self.fps_slider.configure(command=self._on_fps_change)
        
        # Resolution slider
        ctk.CTkLabel(row3_frame, text="Resolution:").grid(row=0, column=2, sticky="w", padx=(20,5), pady=10)
        self.resolution_var = tk.IntVar(value=self.config.get("resolution"))
        resolution_frame = ctk.CTkFrame(row3_frame)
        resolution_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=10)
        
        self.resolution_slider = ctk.CTkSlider(resolution_frame, from_=256, to=1024, variable=self.resolution_var, number_of_steps=3)
        self.resolution_slider.pack(fill="x", padx=5, pady=(10,0))
        self.resolution_label = ctk.CTkLabel(resolution_frame, text=str(self.config.get("resolution")))
        self.resolution_label.pack(pady=(0,10))
        
        self.resolution_slider.configure(command=self._on_resolution_change)
        
        row3_frame.grid_columnconfigure(1, weight=1)
        row3_frame.grid_columnconfigure(3, weight=1)
        
        # Output directory section
        output_frame = ctk.CTkFrame(scroll_frame)
        output_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(output_frame, text="Output Directory", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        dir_frame = ctk.CTkFrame(output_frame)
        dir_frame.pack(fill="x", padx=10, pady=(0,10))
        
        self.output_dir_var = tk.StringVar(value=self.config.get("output_directory"))
        self.output_dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(10,5), pady=10)
        
        self.browse_button = ctk.CTkButton(
            dir_frame, 
            text="Browse", 
            width=80,
            command=self._browse_output_directory
        )
        self.browse_button.pack(side="right", padx=(5,10), pady=10)
        
        # Progress section
        progress_frame = ctk.CTkFrame(scroll_frame)
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(progress_frame, text="Generation Progress", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready")
        self.progress_label.pack(anchor="w", padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0,10))
        self.progress_bar.set(0)
        
        # Control buttons
        button_frame = ctk.CTkFrame(scroll_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        self.generate_button = ctk.CTkButton(
            button_frame,
            text="Generate Video",
            font=("Arial", 14, "bold"),
            height=40,
            command=self._generate_video
        )
        self.generate_button.pack(side="left", padx=10, pady=10)
        
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Arial", 14),
            height=40,
            state="disabled",
            command=self._cancel_generation
        )
        self.cancel_button.pack(side="left", padx=5, pady=10)
        
        self.clear_memory_button = ctk.CTkButton(
            button_frame,
            text="Clear GPU Memory",
            font=("Arial", 14),
            height=40,
            command=self._clear_gpu_memory
        )
        self.clear_memory_button.pack(side="left", padx=5, pady=10)
        
        # Output path display
        output_path_frame = ctk.CTkFrame(scroll_frame)
        output_path_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(output_path_frame, text="Output", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        self.output_path_var = tk.StringVar(value="")
        self.output_path_label = ctk.CTkLabel(output_path_frame, textvariable=self.output_path_var, wraplength=600)
        self.output_path_label.pack(anchor="w", padx=10, pady=(0,10))
        
    def _setup_settings_tab(self):
        """Set up the settings tab"""
        scroll_frame = ctk.CTkScrollableFrame(self.settings_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(scroll_frame)
        theme_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Appearance", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        theme_row = ctk.CTkFrame(theme_frame)
        theme_row.pack(fill="x", padx=10, pady=(0,10))
        
        ctk.CTkLabel(theme_row, text="Theme:").pack(side="left", padx=(10,5), pady=10)
        self.theme_var = tk.StringVar(value=self.config.get("theme", "dark"))
        self.theme_menu = ctk.CTkOptionMenu(theme_row, variable=self.theme_var, values=["dark", "light"])
        self.theme_menu.pack(side="left", padx=5, pady=10)
        self.theme_menu.configure(command=self._on_theme_change)
        
        # Window settings
        window_frame = ctk.CTkFrame(scroll_frame)
        window_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(window_frame, text="Window", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Config actions
        config_frame = ctk.CTkFrame(scroll_frame)
        config_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(config_frame, text="Configuration", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        config_buttons_frame = ctk.CTkFrame(config_frame)
        config_buttons_frame.pack(fill="x", padx=10, pady=(0,10))
        
        ctk.CTkButton(
            config_buttons_frame,
            text="Save Current Settings",
            command=self._save_config
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            config_buttons_frame,
            text="Load Saved Settings",
            command=self._load_saved_config
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            config_buttons_frame,
            text="Reset to Defaults",
            command=self._reset_config
        ).pack(side="left", padx=5, pady=10)
        
    def _setup_console_tab(self):
        """Set up the console/log tab"""
        self.log_pane = LogPane(self.console_tab)
        self.log_pane.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Console controls
        console_controls = ctk.CTkFrame(self.console_tab)
        console_controls.pack(fill="x", padx=10, pady=(0,10))
        
        ctk.CTkButton(
            console_controls,
            text="Clear Console",
            command=self.log_pane.clear
        ).pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(
            console_controls,
            text="Save Log",
            command=self._save_log
        ).pack(side="left", padx=5, pady=10)
        
    def _setup_status_bar(self):
        """Set up the status bar"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready")
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def _setup_menu(self):
        """Set up the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Config", command=self._save_config)
        file_menu.add_command(label="Load Config", command=self._load_saved_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear GPU Memory", command=self._clear_gpu_memory)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _on_steps_change(self, value):
        """Handle steps slider change"""
        self.steps_label.configure(text=str(int(value)))
        
    def _on_fps_change(self, value):
        """Handle FPS slider change"""
        self.fps_label.configure(text=str(int(value)))
        
    def _on_resolution_change(self, value):
        """Handle resolution slider change"""
        self.resolution_label.configure(text=str(int(value)))
        
    def _on_theme_change(self, theme):
        """Handle theme change"""
        ctk.set_appearance_mode(theme)
        self.config.set("theme", theme)
        
    def _browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
            
    def _generate_video(self):
        """Start video generation in a separate thread"""
        if self.is_generating:
            messagebox.showwarning("Warning", "Generation already in progress")
            return
            
        # Get parameters from form
        prompt = self.prompt_textbox.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt")
            return
            
        negative_prompt = self.negative_prompt_textbox.get("1.0", "end-1c").strip()
        output_dir = self.output_dir_var.get().strip()
        
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Save current config
        self._update_config_from_form()
        
        # Disable generate button and enable cancel
        self.generate_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.is_generating = True
        
        # Clear previous output
        self.output_path_var.set("")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starting...")
        
        # Start generation thread
        thread = threading.Thread(
            target=self._run_generation,
            args=(prompt, negative_prompt),
            daemon=True
        )
        thread.start()
        
    def _run_generation(self, prompt, negative_prompt):
        """Run generation in background thread"""
        try:
            # Define callbacks
            def progress_callback(progress: float, message: str):
                self.log_queue.put(("progress", progress, message))
                
            def status_callback(message: str):
                self.log_queue.put(("status", message))
            
            # Get parameters
            params = self._get_current_params()
            
            # Run generation
            output_path = self.pipeline.generate_video(
                prompt=prompt,
                negative_prompt=negative_prompt,
                progress_callback=progress_callback,
                status_callback=status_callback,
                **params
            )
            
            self.log_queue.put(("success", output_path))
            
        except Exception as e:
            self.log_queue.put(("error", str(e), traceback.format_exc()))
        finally:
            self.log_queue.put(("done",))
            
    def _cancel_generation(self):
        """Cancel current generation"""
        if self.is_generating:
            self.pipeline.cancel_generation()
            self.log_pane.log_progress("Cancelling generation...")
            
    def _clear_gpu_memory(self):
        """Clear GPU memory"""
        try:
            self.pipeline.clear_gpu_memory()
            self.log_pane.log_success("GPU memory cleared")
            self.status_label.configure(text="GPU memory cleared")
        except Exception as e:
            self.log_pane.log_error(f"Failed to clear GPU memory: {e}")
            
    def _get_current_params(self):
        """Get current parameters from form"""
        return {
            "sampler": self.sampler_var.get(),
            "scheduler": self.scheduler_var.get(),
            "quantization": self.quantization_var.get(),
            "steps": self.steps_var.get(),
            "fps": self.fps_var.get(),
            "resolution": self.resolution_var.get(),
            "output_dir": self.output_dir_var.get()
        }
        
    def _update_config_from_form(self):
        """Update config from current form values"""
        self.config.set("prompt", self.prompt_textbox.get("1.0", "end-1c"))
        self.config.set("negative_prompt", self.negative_prompt_textbox.get("1.0", "end-1c"))
        
        params = self._get_current_params()
        for key, value in params.items():
            self.config.set(key, value)
            
    def _process_log_queue(self):
        """Process log queue for thread-safe updates"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                
                if message[0] == "progress":
                    _, progress, msg = message
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"{msg} ({progress*100:.1f}%)")
                    self.log_pane.log_progress(msg)
                    
                elif message[0] == "status":
                    _, msg = message
                    self.status_label.configure(text=msg)
                    self.log_pane.log(msg)
                    
                elif message[0] == "success":
                    _, output_path = message
                    self.output_path_var.set(output_path)
                    self.log_pane.log_success(f"Generation complete: {output_path}")
                    self.status_label.configure(text="Generation complete")
                    
                elif message[0] == "error":
                    _, error, traceback_str = message
                    self.log_pane.log_error(f"Generation failed: {error}")
                    self.status_label.configure(text="Generation failed")
                    messagebox.showerror("Generation Error", f"Generation failed:\n{error}")
                    
                elif message[0] == "done":
                    self.generate_button.configure(state="normal")
                    self.cancel_button.configure(state="disabled")
                    self.is_generating = False
                    
        except queue.Empty:
            pass
            
        # Schedule next check
        self.root.after(100, self._process_log_queue)
        
    def _save_config(self):
        """Save current configuration"""
        self._update_config_from_form()
        if self.config.save():
            self.log_pane.log_success("Configuration saved")
            messagebox.showinfo("Success", "Configuration saved successfully")
        else:
            self.log_pane.log_error("Failed to save configuration")
            messagebox.showerror("Error", "Failed to save configuration")
            
    def _load_saved_config(self):
        """Load saved configuration"""
        self.config.load()
        self._apply_config_to_form()
        self.log_pane.log("Configuration loaded")
        
    def _apply_config_to_form(self):
        """Apply config values to form fields"""
        self.prompt_textbox.delete("1.0", "end")
        self.prompt_textbox.insert("1.0", self.config.get("prompt", ""))
        
        self.negative_prompt_textbox.delete("1.0", "end")
        self.negative_prompt_textbox.insert("1.0", self.config.get("negative_prompt", ""))
        
        self.sampler_var.set(self.config.get("sampler"))
        self.scheduler_var.set(self.config.get("scheduler"))
        self.quantization_var.set(self.config.get("quantization"))
        self.steps_var.set(self.config.get("steps"))
        self.fps_var.set(self.config.get("fps"))
        self.resolution_var.set(self.config.get("resolution"))
        self.output_dir_var.set(self.config.get("output_directory"))
        
        # Update slider labels
        self.steps_label.configure(text=str(self.steps_var.get()))
        self.fps_label.configure(text=str(self.fps_var.get()))
        self.resolution_label.configure(text=str(self.resolution_var.get()))
        
    def _reset_config(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset to default settings?"):
            self.config.reset_to_defaults()
            self._apply_config_to_form()
            self.log_pane.log("Configuration reset to defaults")
            
    def _save_log(self):
        """Save console log to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                # Get text from log pane
                log_content = self.log_pane.text_widget.get("1.0", "end-1c")
                with open(filename, 'w') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", "Log saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
            
    def _show_about(self):
        """Show about dialog"""
        about_text = """WanVidGen - Video Generation GUI

Version: 0.1.0

A CustomTkinter-based GUI application for 
video generation with real-time progress 
monitoring and comprehensive logging.

Built with CustomTkinter and threading 
for responsive user experience."""
        
        messagebox.showinfo("About WanVidGen", about_text)
        
    def run(self):
        """Start the GUI application"""
        # Welcome message
        self.log_pane.log("WanVidGen GUI initialized successfully")
        self.log_pane.log("Ready for video generation")
        
        # Start main loop
        self.root.mainloop()


if __name__ == "__main__":
    # This allows running the GUI directly
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    app = WanVidGenGUI()
    app.run()