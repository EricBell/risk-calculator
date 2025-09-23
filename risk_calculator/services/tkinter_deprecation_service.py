"""
Tkinter deprecation service implementation.
Part of Phase 3.4: Validation Services implementation.
"""

from typing import Dict, Any, Optional
import warnings
import sys
import os
import time
import subprocess


class DeprecationLevel:
    """Deprecation warning levels."""
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"


class TkinterDeprecationService:
    """
    Tkinter deprecation service implementing TkinterDeprecationInterface.

    This service manages the deprecation of the Tkinter version and guides
    users to migrate to the Qt-based version.
    """

    def __init__(self):
        """Initialize the Tkinter deprecation service."""
        self._deprecation_active = True
        self._access_count = 0
        self._first_access_time = None
        self._deprecation_level = DeprecationLevel.WARNING

        # Deprecation timeline
        self._deprecation_timeline = {
            "Phase 1 - Warning": "September 2025 - Deprecation warnings shown",
            "Phase 2 - Strong Warning": "October 2025 - Prominent warnings with migration guide",
            "Phase 3 - Deprecation": "November 2025 - Marked as deprecated, Qt recommended",
            "Phase 4 - Removal": "December 2025 - Tkinter version removed"
        }

        # Migration messages
        self._migration_message = self._generate_migration_message()

    def check_tkinter_access(self) -> bool:
        """
        Check if Tkinter version is being accessed.

        Returns:
            True if Tkinter is being accessed, False otherwise
        """
        self._access_count += 1
        if self._first_access_time is None:
            self._first_access_time = time.time()

        # Record this access
        self._log_deprecation_usage({
            'access_number': self._access_count,
            'timestamp': time.time(),
            'caller_info': self._get_caller_info()
        })

        return True

    def show_deprecation_warning(self, level: str = DeprecationLevel.WARNING) -> None:
        """
        Show deprecation warning to user.

        Args:
            level: Warning level (warning, error, block)
        """
        if level == DeprecationLevel.WARNING:
            warnings.warn(
                "The Tkinter version of Risk Calculator is DEPRECATED. "
                "Please use 'python -m risk_calculator.qt_main' instead. "
                "See README.md for Qt installation instructions.",
                DeprecationWarning,
                stacklevel=3
            )

            print("\n" + "="*60)
            print("⚠️  DEPRECATION WARNING")
            print("="*60)
            print("This Tkinter version is DEPRECATED and will be removed.")
            print("Please use the Qt version instead:")
            print("    python -m risk_calculator.qt_main")
            print("="*60 + "\n")

        elif level == DeprecationLevel.ERROR:
            print("\n" + "="*60)
            print("🚨 DEPRECATION ERROR")
            print("="*60)
            print("This Tkinter version is DEPRECATED.")
            print("Migration to Qt version is REQUIRED.")
            print("\nTo use the application:")
            print("    python -m risk_calculator.qt_main")
            print("\nFor help with migration, see README.md")
            print("="*60 + "\n")

        elif level == DeprecationLevel.BLOCK:
            print("\n" + "="*60)
            print("🛑 ACCESS BLOCKED")
            print("="*60)
            print("The Tkinter version has been REMOVED.")
            print("You MUST use the Qt version:")
            print("    python -m risk_calculator.qt_main")
            print("\nFor installation instructions:")
            print("    pip install PySide6")
            print("    See README.md for complete setup")
            print("="*60 + "\n")

            # Exit after showing block message
            sys.exit(1)

    def get_qt_migration_message(self) -> str:
        """
        Get migration message directing users to Qt version.

        Returns:
            Migration message string
        """
        return self._migration_message

    def is_tkinter_blocked(self) -> bool:
        """
        Check if Tkinter access is completely blocked.

        Returns:
            True if blocked, False if still accessible
        """
        return self._deprecation_level == DeprecationLevel.BLOCK

    def log_deprecation_usage(self, context: Dict[str, Any]) -> None:
        """
        Log usage of deprecated Tkinter version.

        Args:
            context: Context information about the usage
        """
        self._log_deprecation_usage(context)

    def get_deprecation_timeline(self) -> Dict[str, str]:
        """
        Get deprecation timeline information.

        Returns:
            Dictionary with deprecation phases and dates
        """
        return self._deprecation_timeline.copy()

    def redirect_to_qt_version(self) -> Optional[int]:
        """
        Attempt to redirect user to Qt version.

        Returns:
            Exit code if redirection attempted, None if not
        """
        print("\n" + "="*60)
        print("🔄 REDIRECTING TO QT VERSION")
        print("="*60)
        print("Attempting to launch Qt-based Risk Calculator...")
        print("="*60 + "\n")

        try:
            # Try to launch Qt version
            result = subprocess.run([
                sys.executable, "-m", "risk_calculator.qt_main"
            ], check=False)

            return result.returncode

        except FileNotFoundError:
            print("❌ Could not launch Qt version.")
            print("Please install Qt dependencies:")
            print("    pip install PySide6")
            print("\nThen run:")
            print("    python -m risk_calculator.qt_main")
            return 1

        except Exception as e:
            print(f"❌ Error launching Qt version: {e}")
            print("Please run manually:")
            print("    python -m risk_calculator.qt_main")
            return 1

    def _generate_migration_message(self) -> str:
        """
        Generate comprehensive migration message.

        Returns:
            Detailed migration message
        """
        return """
MIGRATION TO QT VERSION REQUIRED

The Tkinter version of Risk Calculator is deprecated and will be removed.
Please migrate to the enhanced Qt version.

🔧 QUICK SETUP:
1. Install Qt dependencies:
   pip install PySide6

2. Run the Qt version:
   python -m risk_calculator.qt_main

✨ QT VERSION BENEFITS:
• Better cross-platform support
• High-DPI display compatibility
• Enhanced user interface
• Improved performance and reliability
• Modern UI widgets and styling
• Better window management

📚 COMPLETE SETUP:
See README.md for detailed installation and usage instructions.

🚀 GET STARTED:
The Qt version offers the same powerful risk calculation features
with a significantly improved user experience.

For support, please see the documentation or report issues.
        """.strip()

    def _log_deprecation_usage(self, context: Dict[str, Any]) -> None:
        """
        Internal method to log deprecation usage.

        Args:
            context: Context information about the usage
        """
        # In a production environment, this might log to a file
        # For now, we'll just track the access internally

        # Could write to a log file if needed
        try:
            log_entry = {
                'timestamp': context.get('timestamp', time.time()),
                'access_number': context.get('access_number', self._access_count),
                'caller_info': context.get('caller_info', 'unknown'),
                'deprecation_level': self._deprecation_level,
                'total_accesses': self._access_count
            }

            # In a real implementation, this could be written to:
            # - A log file
            # - A database
            # - A monitoring service
            # - Analytics platform

        except Exception:
            # Silently ignore logging errors to prevent breaking the application
            pass

    def _get_caller_info(self) -> str:
        """
        Get information about the caller for logging.

        Returns:
            String with caller information
        """
        try:
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                caller_frame = frame.f_back.f_back
                filename = caller_frame.f_code.co_filename
                line_number = caller_frame.f_lineno
                function_name = caller_frame.f_code.co_name
                return f"{os.path.basename(filename)}:{function_name}:{line_number}"
        except Exception:
            pass

        return "unknown"

    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about Tkinter usage.

        Returns:
            Dictionary with usage statistics
        """
        current_time = time.time()
        session_duration = current_time - self._first_access_time if self._first_access_time else 0

        return {
            'total_accesses': self._access_count,
            'first_access_time': self._first_access_time,
            'session_duration_seconds': session_duration,
            'deprecation_level': self._deprecation_level,
            'is_blocked': self.is_tkinter_blocked(),
            'deprecation_active': self._deprecation_active
        }

    def set_deprecation_level(self, level: str) -> None:
        """
        Set the deprecation level.

        Args:
            level: New deprecation level
        """
        if level in [DeprecationLevel.WARNING, DeprecationLevel.ERROR, DeprecationLevel.BLOCK]:
            self._deprecation_level = level

    def get_qt_installation_status(self) -> Dict[str, bool]:
        """
        Check Qt installation status.

        Returns:
            Dictionary with installation status information
        """
        status = {
            'pyside6_available': False,
            'qt_main_accessible': False,
            'qt_version': None
        }

        # Check if PySide6 is available
        try:
            import PySide6
            status['pyside6_available'] = True
            status['qt_version'] = PySide6.__version__
        except ImportError:
            pass

        # Check if qt_main module is accessible
        try:
            import risk_calculator.qt_main
            status['qt_main_accessible'] = True
        except ImportError:
            pass

        return status

    def generate_migration_report(self) -> str:
        """
        Generate a comprehensive migration report.

        Returns:
            Detailed migration report as string
        """
        usage_stats = self.get_usage_statistics()
        installation_status = self.get_qt_installation_status()

        report = f"""
TKINTER DEPRECATION REPORT
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

USAGE STATISTICS:
• Total accesses: {usage_stats['total_accesses']}
• Session duration: {usage_stats['session_duration_seconds']:.1f} seconds
• Deprecation level: {usage_stats['deprecation_level']}
• Access blocked: {usage_stats['is_blocked']}

QT INSTALLATION STATUS:
• PySide6 available: {installation_status['pyside6_available']}
• Qt main accessible: {installation_status['qt_main_accessible']}
• Qt version: {installation_status['qt_version'] or 'Not installed'}

MIGRATION RECOMMENDATIONS:
"""

        if not installation_status['pyside6_available']:
            report += "❌ Install PySide6: pip install PySide6\n"
        else:
            report += "✅ PySide6 is installed\n"

        if not installation_status['qt_main_accessible']:
            report += "❌ Qt main module not accessible\n"
        else:
            report += "✅ Qt main module is accessible\n"

        if installation_status['pyside6_available'] and installation_status['qt_main_accessible']:
            report += "\n🚀 Ready to migrate! Run: python -m risk_calculator.qt_main"
        else:
            report += "\n⚠️  Complete Qt installation before migrating"

        return report

    def __repr__(self) -> str:
        """String representation of deprecation service."""
        return (f"TkinterDeprecationService(level={self._deprecation_level}, "
                f"accesses={self._access_count}, blocked={self.is_tkinter_blocked()})")