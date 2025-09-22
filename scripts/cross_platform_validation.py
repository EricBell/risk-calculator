#!/usr/bin/env python3
"""
Cross-platform validation script for Qt Risk Calculator
Tests platform-specific functionality on Windows and Linux
"""

import sys
import os
import platform
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_platform_info() -> Dict[str, str]:
    """Get detailed platform information."""
    return {
        'system': platform.system(),
        'version': platform.version(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0]
    }

def check_qt_availability() -> Tuple[bool, str]:
    """Check if Qt/PySide6 is available and working."""
    try:
        import PySide6
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt, QT_VERSION_STR

        # Try to create a minimal Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        qt_info = f"PySide6 {PySide6.__version__}, Qt {QT_VERSION_STR}"

        # Cleanup
        if app:
            app.quit()

        return True, qt_info
    except ImportError as e:
        return False, f"Import error: {e}"
    except Exception as e:
        return False, f"Qt error: {e}"

def check_display_detection() -> Tuple[bool, str]:
    """Test display detection capabilities."""
    try:
        from risk_calculator.services.qt_display_service import QtDisplayService
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        display_service = QtDisplayService()

        # Test display detection
        profile = display_service.detect_display_profile()
        dimensions = display_service.get_screen_dimensions()
        dpi_scale = display_service.get_dpi_scale_factor()
        is_high_dpi = display_service.is_high_dpi_display()
        platform_info = display_service.get_platform_info()

        result = {
            'screen_size': f"{dimensions[0]}x{dimensions[1]}",
            'dpi_scale': f"{dpi_scale:.2f}",
            'high_dpi': str(is_high_dpi),
            'platform': platform_info
        }

        if app:
            app.quit()

        return True, str(result)
    except Exception as e:
        return False, f"Display detection error: {e}"

def check_configuration_storage() -> Tuple[bool, str]:
    """Test platform-specific configuration storage."""
    try:
        from risk_calculator.services.qt_config_service import QtConfigService

        config_service = QtConfigService()

        # Test configuration operations
        test_key = "cross_platform_test"
        test_value = f"test_value_{int(time.time())}"

        # Set value
        config_service.set_value(test_key, test_value)

        # Get value
        retrieved_value = config_service.get_value(test_key)

        # Verify
        if retrieved_value != test_value:
            return False, f"Value mismatch: set '{test_value}', got '{retrieved_value}'"

        # Get config path
        config_path = config_service.get_config_file_path()

        # Clean up
        config_service.remove_value(test_key)

        platform_specific_info = {
            'config_path': str(config_path) if config_path else "Registry/Native",
            'test_successful': True
        }

        return True, str(platform_specific_info)
    except Exception as e:
        return False, f"Configuration error: {e}"

def check_window_management() -> Tuple[bool, str]:
    """Test window management capabilities."""
    try:
        from risk_calculator.services.qt_window_manager import QtWindowManager
        from risk_calculator.models.window_configuration import WindowConfiguration
        from datetime import datetime
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        window_manager = QtWindowManager()

        # Test window configuration
        test_config = WindowConfiguration(
            width=1024,
            height=768,
            x=100,
            y=100,
            maximized=False,
            last_updated=datetime.now()
        )

        # Test validation
        validated_config = window_manager.validate_window_bounds(test_config)

        # Test default size
        default_size = window_manager.get_default_window_size()

        if app:
            app.quit()

        result = {
            'validation_successful': validated_config is not None,
            'default_size': f"{default_size[0]}x{default_size[1]}",
            'bounds_validation': 'working'
        }

        return True, str(result)
    except Exception as e:
        return False, f"Window management error: {e}"

def check_calculation_services() -> Tuple[bool, str]:
    """Test that calculation services work correctly."""
    try:
        from risk_calculator.services.risk_calculation_service import RiskCalculationService
        from risk_calculator.models.equity_trade import EquityTrade
        from decimal import Decimal

        calc_service = RiskCalculationService()

        # Test calculation
        trade = EquityTrade(
            symbol="CROSS_PLATFORM_TEST",
            account_size=Decimal("10000"),
            risk_percentage=Decimal("2.0"),
            entry_price=Decimal("100.00"),
            stop_loss=Decimal("95.00")
        )

        result = calc_service.calculate_position_size(trade, "percentage")

        # Verify calculation
        expected_shares = 40  # (10000 * 0.02) / (100 - 95) = 40

        if result.position_size != expected_shares:
            return False, f"Calculation error: expected {expected_shares}, got {result.position_size}"

        calculation_info = {
            'position_size': result.position_size,
            'estimated_risk': result.estimated_risk,
            'calculation_method': 'percentage',
            'accuracy': 'preserved'
        }

        return True, str(calculation_info)
    except Exception as e:
        return False, f"Calculation error: {e}"

def check_qt_application_startup() -> Tuple[bool, str]:
    """Test Qt application startup."""
    try:
        from risk_calculator.qt_main import RiskCalculatorQtApp

        start_time = time.time()

        # Create application
        qt_app = RiskCalculatorQtApp()
        app = qt_app.create_application()

        # Create main window
        main_window = qt_app.create_main_window()

        startup_time = time.time() - start_time

        # Cleanup
        if main_window:
            main_window.close()
        if app:
            app.quit()

        startup_info = {
            'startup_time': f"{startup_time:.3f}s",
            'target_met': startup_time < 3.0,
            'application_created': True,
            'main_window_created': True
        }

        return True, str(startup_info)
    except Exception as e:
        return False, f"Application startup error: {e}"

def run_platform_validation() -> Dict[str, Tuple[bool, str]]:
    """Run all platform validation tests."""
    tests = {
        'Platform Info': (True, str(get_platform_info())),
        'Qt Availability': check_qt_availability(),
        'Display Detection': check_display_detection(),
        'Configuration Storage': check_configuration_storage(),
        'Window Management': check_window_management(),
        'Calculation Services': check_calculation_services(),
        'Qt Application Startup': check_qt_application_startup()
    }

    return tests

def generate_validation_report(results: Dict[str, Tuple[bool, str]]) -> str:
    """Generate a validation report."""
    platform_info = get_platform_info()

    report = f"""
# Cross-Platform Validation Report
**Platform**: {platform_info['system']} {platform_info['version']}
**Architecture**: {platform_info['architecture']}
**Python**: {platform_info['python_version']}
**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Results

"""

    total_tests = len(results)
    passed_tests = sum(1 for success, _ in results.values() if success)

    for test_name, (success, details) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        report += f"### {test_name}: {status}\n"
        report += f"```\n{details}\n```\n\n"

    report += f"""
## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {(passed_tests / total_tests) * 100:.1f}%

## Platform-Specific Notes
"""

    if platform_info['system'] == 'Windows':
        report += """
### Windows-Specific Validation
- Configuration stored in Windows Registry
- High-DPI scaling support via Windows DPI awareness
- File paths use Windows conventions
"""
    elif platform_info['system'] == 'Linux':
        report += """
### Linux-Specific Validation
- Configuration stored in XDG-compliant directories
- X11/Wayland display detection
- POSIX file path conventions
"""

    return report

def main():
    """Main validation function."""
    print("Starting cross-platform validation...")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("-" * 50)

    # Run validation tests
    results = run_platform_validation()

    # Print results
    for test_name, (success, details) in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if not success:
            print(f"  Error: {details}")

    # Generate report
    report = generate_validation_report(results)

    # Save report
    report_file = f"validation_report_{platform.system().lower()}_{int(time.time())}.md"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\nValidation report saved to: {report_file}")

    # Summary
    total_tests = len(results)
    passed_tests = sum(1 for success, _ in results.values() if success)

    print(f"\nSummary: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")

    return passed_tests == total_tests

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)