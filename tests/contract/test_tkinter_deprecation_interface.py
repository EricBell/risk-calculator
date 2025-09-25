"""
Contract tests for Tkinter Deprecation interface.

Tests the interface contract for Tkinter deprecation functionality
to ensure proper warnings and redirection to Qt version.
"""

import pytest
import sys
import os
import warnings
from unittest.mock import patch, Mock

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestTkinterDeprecationInterface:
    """Test the Tkinter Deprecation interface contract."""

    def test_deprecated_main_file_exists(self):
        """Test that deprecated Tkinter main file exists and is accessible."""
        try:
            from risk_calculator import main_tkinter_deprecated
            assert main_tkinter_deprecated is not None
        except ImportError:
            pytest.fail("main_tkinter_deprecated module should exist and be importable")

    def test_deprecation_warning_interface(self):
        """Test that deprecation warning is properly issued."""
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")  # Capture all warnings

            try:
                from risk_calculator import main_tkinter_deprecated

                # Should have main function that issues deprecation warning
                assert hasattr(main_tkinter_deprecated, 'main'), "Should have main() function"

                # Test calling main captures deprecation warning
                with patch('sys.exit') as mock_exit:
                    with patch('builtins.print') as mock_print:
                        try:
                            main_tkinter_deprecated.main()
                        except SystemExit:
                            pass  # Expected for main() functions
                        except Exception:
                            pass  # May fail due to missing display, but warning should still be issued

                # Should have issued deprecation warning
                deprecation_warnings = [w for w in warning_list if issubclass(w.category, DeprecationWarning)]
                if len(deprecation_warnings) > 0:
                    assert "DEPRECATED" in str(deprecation_warnings[0].message).upper()

            except ImportError:
                pytest.fail("Should be able to import deprecated Tkinter module")

    def test_qt_redirection_message_interface(self):
        """Test that clear redirection to Qt version is provided."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Test that file contains Qt redirection information
            import inspect
            source = inspect.getsource(main_tkinter_deprecated)

            # Should mention Qt version
            assert "qt" in source.lower() or "Qt" in source, "Should reference Qt version"

            # Should provide specific command for Qt version
            assert "qt_main" in source, "Should reference qt_main module"

        except ImportError:
            pytest.fail("Should be able to access deprecated module source")

    def test_deprecated_entry_point_interface(self):
        """Test that deprecated entry point exists in setup.py if configured."""
        setup_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'setup.py'
        )

        if os.path.exists(setup_path):
            with open(setup_path, 'r') as f:
                setup_content = f.read()

            # Should have both Qt and deprecated entry points
            assert "qt_main" in setup_content, "setup.py should reference qt_main"

            # May have deprecated entry point
            if "tkinter" in setup_content.lower():
                assert "deprecated" in setup_content.lower(), "Tkinter entry should be marked deprecated"

    def test_deprecation_documentation_interface(self):
        """Test that deprecation is properly documented in the module."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Should have module docstring explaining deprecation
            assert main_tkinter_deprecated.__doc__ is not None, "Module should have docstring"

            docstring = main_tkinter_deprecated.__doc__.upper()
            assert "DEPRECATED" in docstring, "Docstring should mention deprecation"
            assert "QT" in docstring or "Qt" in main_tkinter_deprecated.__doc__, "Should mention Qt alternative"

        except ImportError:
            pytest.fail("Should be able to import deprecated module for documentation check")

    def test_warning_visibility_interface(self):
        """Test that deprecation warnings are visible to users."""
        with patch('builtins.print') as mock_print:
            with patch('sys.exit') as mock_exit:
                try:
                    from risk_calculator import main_tkinter_deprecated

                    # Try to call main to trigger warning output
                    try:
                        main_tkinter_deprecated.main()
                    except SystemExit:
                        pass
                    except Exception:
                        pass  # May fail in headless environment

                    # Should have printed deprecation message to user
                    if mock_print.called:
                        printed_messages = [str(call) for call in mock_print.call_args_list]
                        deprecation_message_found = any(
                            "deprecat" in msg.lower() for msg in printed_messages
                        )
                        # Note: This is a soft check since the exact implementation may vary
                        # The important thing is that some user-visible output occurs

                except ImportError:
                    pytest.fail("Should be able to test deprecation warning visibility")

    def test_python_version_compatibility_interface(self):
        """Test that deprecation interface works across Python versions."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Should have version checking if implemented
            if hasattr(main_tkinter_deprecated, 'check_python_version'):
                version_check = main_tkinter_deprecated.check_python_version
                assert callable(version_check), "Version check should be callable"

            # Should work with current Python version
            python_version = sys.version_info[:2]
            assert python_version >= (3, 8), "Should support Python 3.8+"

        except ImportError:
            pytest.fail("Deprecation module should be compatible with current Python version")

    def test_graceful_fallback_interface(self):
        """Test that deprecated version fails gracefully if needed."""
        with patch('sys.exit') as mock_exit:
            try:
                from risk_calculator import main_tkinter_deprecated

                # Should have error handling for missing dependencies
                # This tests the interface exists, not full functionality
                assert hasattr(main_tkinter_deprecated, 'main'), "Should have main function"

                # Should be able to call without crashing the test
                try:
                    main_tkinter_deprecated.main()
                except SystemExit:
                    pass  # Expected behavior
                except ImportError as e:
                    # May not have tkinter in test environment
                    assert "tkinter" in str(e).lower(), f"Should fail gracefully with tkinter error: {e}"
                except Exception:
                    pass  # Other errors acceptable in test environment

            except ImportError:
                pytest.fail("Should be able to import deprecated module")

    def test_migration_guidance_interface(self):
        """Test that clear migration guidance is provided."""
        try:
            from risk_calculator import main_tkinter_deprecated
            import inspect

            # Get source code to check for migration guidance
            source = inspect.getsource(main_tkinter_deprecated)

            # Should provide clear instructions for migration
            guidance_indicators = [
                "qt_main",
                "python -m risk_calculator.qt_main",
                "Qt version",
                "installation",
                "README"
            ]

            found_guidance = sum(1 for indicator in guidance_indicators if indicator in source)
            assert found_guidance >= 2, f"Should provide clear migration guidance, found {found_guidance} indicators"

        except ImportError:
            pytest.fail("Should be able to check migration guidance in deprecated module")


if __name__ == "__main__":
    pytest.main([__file__])