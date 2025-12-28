"""Main application entry point with Flet."""

import sys
import os
import logging
from pathlib import Path

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flet as ft
from risk_calculator.views.main_view import MainView
from risk_calculator.controllers.main_controller import MainController


# Version information
__version__ = "1.0.0"


def setup_logging(debug: bool = False) -> None:
    """Setup application logging."""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure logging level
    level = logging.DEBUG if debug else logging.INFO

    # Configure logging
    log_file = log_dir / "risk_calculator.log"
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(f"Risk Calculator v{__version__} starting...")
    if debug:
        logger.debug("Debug mode enabled")


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    min_version = (3, 10)  # Flet requires Python 3.10+
    current_version = sys.version_info[:2]

    if current_version < min_version:
        error_msg = (
            f"Python {min_version[0]}.{min_version[1]}+ is required. "
            f"Current version is {current_version[0]}.{current_version[1]}."
        )
        print(f"Error: {error_msg}")
        return False

    return True


def main_app(page: ft.Page):
    """Flet application entry point."""
    logger = logging.getLogger(__name__)
    logger.info("Initializing Flet application")

    # Configure page
    page.title = "Risk Calculator - Daytrading Position Sizing"
    page.window_width = 900
    page.window_height = 800
    page.window_min_width = 700
    page.window_min_height = 600
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Set theme
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True
    )

    try:
        # Create MVC components
        main_view = MainView()
        main_controller = MainController(main_view)
        main_view.main_controller = main_controller

        # Wire up page reference
        main_view.page = page

        # Build and add main view to page
        main_container = main_view.build()
        page.add(main_container)

        # Wire up page references to child views after build
        if main_view.equity_view:
            main_view.equity_view.page = page
        if main_view.options_view:
            main_view.options_view.page = page
        if main_view.futures_view:
            main_view.futures_view.page = page

        page.update()

        logger.info("Application initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        # Show error in page
        page.add(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Application Error", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR),
                    ft.Text(f"Failed to start: {str(e)}", color=ft.Colors.ERROR),
                    ft.Text("Check the log file for details.", size=12, italic=True)
                ])
            )
        )
        page.update()


def run_app(debug: bool = False):
    """Run the Flet application."""
    setup_logging(debug)

    if not check_python_version():
        return 1

    logger = logging.getLogger(__name__)

    try:
        # Run Flet in web browser (works on all systems, no native dependencies)
        logger.info("Starting Risk Calculator application")
        logger.info("Application will open in your default web browser at http://localhost:8550")
        ft.app(target=main_app, view=ft.AppView.WEB_BROWSER, port=8550)
        logger.info("Application closed normally")
        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Uncaught exception: {e}", exc_info=True)
        print(f"Critical error: {type(e).__name__}: {e}")
        print("Check the log file for details.")
        return 1


def show_version():
    """Show version information."""
    print(f"Risk Calculator v{__version__}")
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Flet {ft.__version__}")
    print(f"Platform: {sys.platform}")


def main() -> int:
    """Main entry point with CLI argument handling."""
    # Handle command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['--version', '-v']:
            show_version()
            return 0

        elif arg in ['--debug', '-d']:
            print("Starting in debug mode...")
            return run_app(debug=True)

        elif arg in ['--help', '-h']:
            print("""Risk Calculator - Daytrading Position Sizing Tool

Usage:
    python -m risk_calculator.main [options]

Options:
    --version, -v    Show version information
    --debug, -d      Run in debug mode with verbose logging
    --help, -h       Show this help message

Examples:
    python -m risk_calculator.main              # Run normally
    python -m risk_calculator.main --debug      # Run with debug logging
    python -m risk_calculator.main --version    # Show version info
""")
            return 0

        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            return 1

    # Run normally
    return run_app()


if __name__ == "__main__":
    sys.exit(main())
