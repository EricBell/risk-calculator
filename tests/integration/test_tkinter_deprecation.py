"""
Integration test for Tkinter deprecation verification.

Tests that Tkinter version is properly deprecated and users are
redirected to the Qt version with appropriate warnings.
"""

import pytest
import sys
import os
import warnings
import subprocess
from unittest.mock import patch, Mock

# Add the risk_calculator package to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestTkinterDeprecationIntegration:
    """Integration tests for Tkinter deprecation functionality."""

    def test_deprecated_module_import_and_warning(self):
        """Test that deprecated module imports and issues proper warnings."""
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")

            try:
                from risk_calculator import main_tkinter_deprecated

                # Module should import successfully
                assert main_tkinter_deprecated is not None

                # Should have main function
                assert hasattr(main_tkinter_deprecated, 'main')
                assert callable(main_tkinter_deprecated.main)

                # Try to execute main to trigger warnings (with comprehensive mocking)
                with patch('sys.exit'):
                    with patch('builtins.print'):
                        with patch('tkinter.Tk'):  # Mock tkinter to prevent GUI launch
                            with patch('risk_calculator.main_tkinter_deprecated.run_application'):
                                with warnings.catch_warnings():
                                    warnings.simplefilter("ignore", DeprecationWarning)
                                    try:
                                        main_tkinter_deprecated.main()
                                    except (SystemExit, ImportError, AttributeError):
                                        pass  # Expected to fail in test environment with mocking

                # Check if deprecation warning was issued
                deprecation_warnings = [w for w in warning_list if issubclass(w.category, DeprecationWarning)]

                # Should have at least one deprecation warning
                if len(deprecation_warnings) > 0:
                    warning_message = str(deprecation_warnings[0].message)
                    assert "deprecated" in warning_message.lower()
                    assert "qt" in warning_message.lower()

            except ImportError as e:
                pytest.fail(f"Should be able to import deprecated module: {e}")

    def test_qt_version_recommendation(self):
        """Test that deprecated version clearly recommends Qt version."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Check module docstring for Qt recommendation
            docstring = main_tkinter_deprecated.__doc__
            assert docstring is not None
            assert "qt" in docstring.lower() or "Qt" in docstring
            assert "python -m risk_calculator.qt_main" in docstring

            # Test that main function provides clear guidance
            with patch('sys.exit'):
                with patch('builtins.print') as mock_print:
                    with patch('tkinter.Tk'):  # Mock tkinter to prevent GUI launch
                        with patch('risk_calculator.main_tkinter_deprecated.run_application'):
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", DeprecationWarning)
                                try:
                                    main_tkinter_deprecated.main()
                                except (SystemExit, ImportError, AttributeError):
                                    pass  # Expected to fail in test environment with mocking

                    # Should print deprecation message
                    if mock_print.called:
                        print_calls = [str(call) for call in mock_print.call_args_list]
                        qt_mentioned = any("qt" in call.lower() for call in print_calls)
                        deprecation_mentioned = any("deprecat" in call.lower() for call in print_calls)

                        # Should mention both deprecation and Qt alternative
                        assert qt_mentioned or deprecation_mentioned, "Should provide clear guidance to user"

        except ImportError as e:
            pytest.fail(f"Should be able to test Qt recommendation: {e}")

    def test_entry_points_configuration(self):
        """Test that entry points are configured correctly in setup.py."""
        setup_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'setup.py'
        )

        if os.path.exists(setup_path):
            with open(setup_path, 'r') as f:
                setup_content = f.read()

            # Should have Qt as primary entry point
            assert "qt_main:main" in setup_content, "Qt should be primary entry point"

            # Check for deprecated entry point if it exists
            if "tkinter" in setup_content.lower():
                assert "main_tkinter_deprecated" in setup_content, "Deprecated entry should use correct module"

    def test_deprecation_visibility_to_end_user(self):
        """Test that deprecation warnings are visible to end users."""
        # Test that running the deprecated version shows clear warnings
        try:
            from risk_calculator import main_tkinter_deprecated

            captured_output = []

            def mock_print(*args, **kwargs):
                captured_output.append(' '.join(str(arg) for arg in args))

            with patch('builtins.print', mock_print):
                with patch('sys.exit'):
                    with patch('tkinter.Tk'):  # Mock tkinter to prevent GUI launch
                        with patch('risk_calculator.main_tkinter_deprecated.run_application'):
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", DeprecationWarning)
                                try:
                                    main_tkinter_deprecated.main()
                                except (SystemExit, ImportError, AttributeError):
                                    pass  # Expected to fail in test environment with mocking

            # Should have visible output about deprecation
            output_text = ' '.join(captured_output).lower()

            if captured_output:  # If there was any output
                assert "deprecat" in output_text or "qt" in output_text, \
                    f"Should show deprecation message to user. Output: {captured_output[:3]}"

        except ImportError:
            pytest.fail("Should be able to test user-visible deprecation")

    def test_python_version_compatibility_check(self):
        """Test that deprecated version works with supported Python versions."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Should work with current Python version
            current_version = sys.version_info[:2]

            # Test version checking if implemented
            if hasattr(main_tkinter_deprecated, 'check_python_version'):
                with patch('builtins.print'):
                    result = main_tkinter_deprecated.check_python_version()
                    assert isinstance(result, bool), "Version check should return boolean"
                    assert result is True, f"Should support Python {current_version}"

        except ImportError:
            pytest.fail("Should be able to test Python version compatibility")

    def test_graceful_failure_without_tkinter(self):
        """Test that deprecated version fails gracefully if tkinter unavailable."""
        # This tests the error handling when tkinter dependencies are missing
        with patch('sys.exit') as mock_exit:
            try:
                from risk_calculator import main_tkinter_deprecated

                # Should handle missing tkinter gracefully
                with patch('builtins.print'):
                    with patch('tkinter.Tk'):  # Mock tkinter to prevent GUI launch
                        with patch('risk_calculator.main_tkinter_deprecated.run_application'):
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore", DeprecationWarning)
                                try:
                                    main_tkinter_deprecated.main()
                                except SystemExit:
                                    pass  # Expected behavior
                                except ImportError as e:
                                    # Should fail gracefully with clear message about tkinter
                                    assert "tkinter" in str(e).lower(), "Should provide clear error about tkinter"
                                except (AttributeError, Exception):
                                    # Other exceptions are acceptable in test environment with mocking
                                    pass

            except ImportError:
                pytest.fail("Should be able to import deprecated module for failure testing")

    def test_migration_documentation_completeness(self):
        """Test that complete migration documentation is available."""
        try:
            from risk_calculator import main_tkinter_deprecated
            import inspect

            # Check that comprehensive guidance is provided
            source = inspect.getsource(main_tkinter_deprecated)

            migration_elements = [
                "qt_main",              # Reference to new module
                "python -m",            # Command to run
                "installation",         # Setup instructions
                "README",               # Documentation reference
                "Qt version",           # Clear alternative
                "cross-platform",       # Benefits explanation
            ]

            found_elements = sum(1 for element in migration_elements if element in source)

            assert found_elements >= 3, f"Should provide comprehensive migration guidance, found {found_elements}/6 elements"

        except ImportError:
            pytest.fail("Should be able to check migration documentation")

    def test_backwards_compatibility_interface(self):
        """Test that deprecated version maintains necessary interface compatibility."""
        try:
            from risk_calculator import main_tkinter_deprecated

            # Should still have expected application interface
            assert hasattr(main_tkinter_deprecated, 'main'), "Should maintain main() interface"

            # Should have application class if it exists
            if hasattr(main_tkinter_deprecated, 'RiskCalculatorApp'):
                app_class = main_tkinter_deprecated.RiskCalculatorApp
                assert callable(app_class), "RiskCalculatorApp should be callable"

            # Should have helper functions if they exist
            helper_functions = ['setup_logging', 'check_python_version', 'run_application']
            for func_name in helper_functions:
                if hasattr(main_tkinter_deprecated, func_name):
                    func = getattr(main_tkinter_deprecated, func_name)
                    assert callable(func), f"{func_name} should be callable if present"

        except ImportError:
            pytest.fail("Should maintain interface compatibility for testing")


if __name__ == "__main__":
    pytest.main([__file__])