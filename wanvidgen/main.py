"""
Main entry point for WanVidGen application
"""

import sys
import logging
import traceback
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wanvidgen.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    try:
        logger.info("Starting WanVidGen application")
        
        # Import and run GUI
        from wanvidgen.gui import WanVidGenGUI
        
        logger.info("Initializing GUI")
        app = WanVidGenGUI()
        
        logger.info("Starting GUI main loop")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        
        # Show user-friendly error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            error_message = f"An unexpected error occurred:\n\n{str(e)}\n\nCheck wanvidgen.log for details."
            messagebox.showerror("Application Error", error_message)
            
        except Exception:
            pass  # If we can't show the error dialog, just exit
            
    finally:
        logger.info("WanVidGen application exiting")


if __name__ == "__main__":
    main()