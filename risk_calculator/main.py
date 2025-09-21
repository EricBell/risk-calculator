"""Main application entry point with cross-platform Tkinter setup."""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from pathlib import Path

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_calculator.views.main_window import MainWindow
from risk_calculator.controllers.enhanced_main_controller import EnhancedMainController


class RiskCalculatorApp:
    """Main application class for testing and programmatic access."""

    def __init__(self):
        self.main_window = None
        self.main_controller = None

    def create_components(self):
        """Create application components without running GUI."""
        self.main_window = MainWindow()
        self.main_controller = EnhancedMainController(self.main_window)
        self.main_window.set_controller(self.main_controller)
        return self.main_window, self.main_controller

    def run(self):
        """Run the application."""
        if not self.main_window:
            self.create_components()
        self.main_window.run()


def setup_logging() -> None:
    """Setup application logging."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = log_dir / "risk_calculator.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Risk Calculator application starting...")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    min_version = (3, 8)
    current_version = sys.version_info[:2]

    if current_version < min_version:
        error_msg = (
            f"Python {min_version[0]}.{min_version[1]}+ is required. "
            f"Current version is {current_version[0]}.{current_version[1]}."
        )
        print(f"Error: {error_msg}")
        return False

    return True


def setup_cross_platform_config() -> dict:
    """Setup cross-platform configuration."""
    config = {
        'platform': sys.platform,
        'high_dpi_aware': False,
        'theme': 'default'
    }

    # Windows-specific setup
    if sys.platform == 'win32':
        try:
            # Enable high DPI awareness on Windows
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            config['high_dpi_aware'] = True
        except Exception:
            pass  # Ignore if not available

        # Set Windows-specific theme
        config['theme'] = 'vista'

    # Linux-specific setup
    elif sys.platform.startswith('linux'):
        # Set Linux-specific theme
        config['theme'] = 'clam'

    # macOS-specific setup (future support)
    elif sys.platform == 'darwin':
        config['theme'] = 'aqua'

    return config


def configure_tkinter_defaults() -> None:
    """Configure Tkinter default settings for better cross-platform appearance."""
    try:
        # Set default font size for better readability
        default_font = ('TkDefaultFont', 9)

        # Configure default widget options
        tk_defaults = {
            'Button': {'font': default_font},
            'Label': {'font': default_font},
            'Entry': {'font': default_font},
            'Text': {'font': ('TkFixedFont', 9)},
            'Listbox': {'font': default_font}
        }

        # Apply defaults (this is a placeholder - actual implementation would
        # require configuring the root window's option_add method)

    except Exception as e:
        logging.getLogger(__name__).warning(f"Could not configure Tkinter defaults: {e}")


def handle_uncaught_exception(exc_type, exc_value, exc_traceback) -> None:
    """Handle uncaught exceptions globally."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Let keyboard interrupt exit normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger = logging.getLogger(__name__)
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Show error dialog if possible
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        error_msg = (
            f"An unexpected error occurred:\n\n"
            f"{exc_type.__name__}: {exc_value}\n\n"
            f"The application will now exit.\n"
            f"Check the log file for details."
        )

        messagebox.showerror("Application Error", error_msg)
        root.destroy()

    except Exception:
        # If GUI error dialog fails, print to console
        print(f"Critical error: {exc_type.__name__}: {exc_value}")

    sys.exit(1)


def create_application() -> tuple:
    """Create and configure the main application components."""
    logger = logging.getLogger(__name__)

    try:
        # Create main window first (without controller)
        main_window = MainWindow()
        logger.info("Main window created successfully")

        # Create main controller with window reference
        main_controller = EnhancedMainController(main_window)
        logger.info("Main controller created successfully")

        # Connect controller to window and recreate tabs with controllers
        main_window.set_controller(main_controller)
        logger.info("Controller connected to main window")

        return main_window, main_controller

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def run_application() -> None:
    """Run the main application."""
    logger = logging.getLogger(__name__)

    try:
        # Create application components
        main_window, main_controller = create_application()

        # Log system information
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Tkinter version: {tk.TkVersion}")

        # Run the application
        logger.info("Starting main application loop")
        main_window.run()

    except Exception as e:
        logger.error(f"Application runtime error: {e}")
        raise

    finally:
        logger.info("Application shutting down")


def main() -> int:
    """Main entry point."""
    try:
        # Check Python version compatibility
        if not check_python_version():
            return 1

        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)

        # Setup global exception handler
        sys.excepthook = handle_uncaught_exception

        # Get cross-platform configuration
        config = setup_cross_platform_config()
        logger.info(f"Platform configuration: {config}")

        # Configure Tkinter defaults
        configure_tkinter_defaults()

        # Run the application
        run_application()

        return 0

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 130  # Standard exit code for Ctrl+C

    except ImportError as e:
        error_msg = f"Required module not found: {e}"
        print(f"Error: {error_msg}")
        logging.getLogger(__name__).error(error_msg)
        return 1

    except Exception as e:
        error_msg = f"Application startup failed: {e}"
        print(f"Error: {error_msg}")
        logging.getLogger(__name__).error(error_msg)
        return 1


# Development and debugging functions
def run_in_debug_mode() -> None:
    """Run application in debug mode with enhanced logging."""
    # Set debug logging level
    logging.getLogger().setLevel(logging.DEBUG)

    # Enable Tkinter debug mode
    os.environ['TK_DEBUG'] = '1'

    print("Running in debug mode...")
    main()


def run_tests() -> int:
    """Run application tests (if available)."""
    try:
        import pytest
        return pytest.main(['-v', 'tests/'])
    except ImportError:
        print("pytest not available - cannot run tests")
        return 1


def show_version() -> None:
    """Show application version information."""
    print("Risk Calculator v1.0")
    print(f"Python {sys.version}")
    print(f"Tkinter {tk.TkVersion}")
    print(f"Platform: {sys.platform}")


# Command line interface
if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['--version', '-v']:
            show_version()
            sys.exit(0)
        elif arg in ['--debug', '-d']:
            run_in_debug_mode()
            sys.exit(0)
        elif arg in ['--test', '-t']:
            sys.exit(run_tests())
        elif arg in ['--help', '-h']:
            print("""Risk Calculator - Daytrading Position Sizing Tool

Usage:
    python main.py [options]

Options:
    --version, -v    Show version information
    --debug, -d      Run in debug mode
    --test, -t       Run tests
    --help, -h       Show this help message

Examples:
    python main.py              # Run normally
    python main.py --debug      # Run with debug logging
    python main.py --version    # Show version info
""")
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            sys.exit(1)

    # Run normally
    sys.exit(main())