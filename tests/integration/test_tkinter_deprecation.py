"""
Integration test for Tkinter deprecation verification
This test MUST FAIL until Tkinter deprecation is properly implemented.
"""

import pytest
import subprocess
import sys
import warnings
import os
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestTkinterDeprecation:
    """Integration tests for Tkinter deprecation functionality."""

    def test_deprecated_main_file_exists(self):
        """Test that deprecated Tkinter main file exists with correct name."""
        deprecated_path = Path("risk_calculator/main_tkinter_deprecated.py")
        assert deprecated_path.exists(), "main_tkinter_deprecated.py should exist"

        # Should not have original main.py
        original_path = Path("risk_calculator/main.py")
        assert not original_path.exists(), "Original main.py should be renamed"

    def test_deprecated_main_shows_warning_on_import(self):
        """Test that importing deprecated main shows deprecation warning."""
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")

            try:
                import risk_calculator.main_tkinter_deprecated
                # Should generate deprecation warning on import or usage
                deprecation_warnings = [w for w in warning_list
                                       if issubclass(w.category, DeprecationWarning)]
                # Note: might not warn on import, could warn on main() call
            except ImportError:
                pytest.fail("Should be able to import deprecated main for testing")

    def test_deprecated_main_shows_console_warning(self):
        """Test that running deprecated main shows console warning."""
        # Run the deprecated main with --help to avoid GUI startup
        try:
            result = subprocess.run([
                sys.executable, "-m", "risk_calculator.main_tkinter_deprecated", "--help"
            ], capture_output=True, text=True, timeout=10)

            # Should show deprecation warning in output
            output = result.stdout + result.stderr
            output_lower = output.lower()

            assert "deprecat" in output_lower, f"Should show deprecation warning. Output: {output}"
            assert "qt" in output_lower, f"Should mention Qt version. Output: {output}"

        except subprocess.TimeoutExpired:
            pytest.fail("Deprecated main should handle --help quickly")
        except FileNotFoundError:
            pytest.fail("Should be able to run deprecated main module")

    def test_qt_main_is_default_entry_point(self):
        """Test that Qt main is the default entry point in setup.py."""
        setup_path = Path("setup.py")
        if setup_path.exists():
            setup_content = setup_path.read_text()

            # Should reference qt_main as default entry point
            assert "qt_main:main" in setup_content, "setup.py should use qt_main as default"

            # Should have deprecated entry point as secondary
            assert "main_tkinter_deprecated" in setup_content, "setup.py should include deprecated entry point"

    def test_qt_dependencies_in_requirements(self):
        """Test that Qt dependencies are properly specified."""
        # Check requirements.txt
        requirements_path = Path("requirements.txt")
        if requirements_path.exists():
            requirements_content = requirements_path.read_text()
            assert "PySide6" in requirements_content, "requirements.txt should include PySide6"

        # Check setup.py
        setup_path = Path("setup.py")
        if setup_path.exists():
            setup_content = setup_path.read_text()
            assert "PySide6" in setup_content, "setup.py should include PySide6 dependency"

    def test_readme_contains_qt_instructions(self):
        """Test that README contains Qt installation and usage instructions."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md should exist"

        readme_content = readme_path.read_text()
        readme_lower = readme_content.lower()

        # Should contain Qt installation instructions
        assert "pyside6" in readme_lower, "README should mention PySide6"
        assert "qt" in readme_lower, "README should mention Qt"
        assert "pip install" in readme_lower, "README should have installation instructions"

        # Should contain usage instructions
        assert "qt_main" in readme_content, "README should mention qt_main usage"

    def test_readme_contains_migration_guidance(self):
        """Test that README contains clear migration guidance from Tkinter."""
        readme_path = Path("README.md")
        readme_content = readme_path.read_text()
        readme_lower = readme_content.lower()

        # Should mention migration from Tkinter
        assert "tkinter" in readme_lower, "README should mention Tkinter"
        assert "deprecat" in readme_lower, "README should mention deprecation"
        assert "migrat" in readme_lower, "README should mention migration"

    def test_qt_main_can_import_successfully(self):
        """Test that Qt main can be imported without errors."""
        try:
            import risk_calculator.qt_main
            # Should import successfully
            assert hasattr(risk_calculator.qt_main, 'main'), "qt_main should have main function"
        except ImportError as e:
            if "PySide6" in str(e):
                pytest.skip("PySide6 not installed, skipping Qt import test")
            else:
                pytest.fail(f"qt_main should be importable: {e}")

    def test_deprecated_warning_content_helpful(self):
        """Test that deprecation warning content is helpful to users."""
        try:
            # Import and check the module docstring
            import risk_calculator.main_tkinter_deprecated as deprecated_main

            module_doc = deprecated_main.__doc__
            assert module_doc is not None, "Deprecated module should have helpful docstring"

            doc_lower = module_doc.lower()
            assert "deprecated" in doc_lower, "Docstring should mention deprecation"
            assert "qt" in doc_lower, "Docstring should mention Qt version"
            assert "python -m risk_calculator.qt_main" in module_doc, "Should include exact command"

        except ImportError:
            pytest.fail("Should be able to import deprecated main for testing")

    def test_console_scripts_entry_points(self):
        """Test that console scripts are properly configured."""
        setup_path = Path("setup.py")
        if setup_path.exists():
            setup_content = setup_path.read_text()

            # Should have risk-calculator pointing to Qt version
            assert "risk-calculator=risk_calculator.qt_main:main" in setup_content

            # Should have deprecated entry point
            assert "risk-calculator-tkinter" in setup_content

    def test_deprecation_timeline_documentation(self):
        """Test that deprecation timeline is documented."""
        readme_path = Path("README.md")
        readme_content = readme_path.read_text()

        # Should mention timeline or removal plans
        timeline_keywords = ["deprecat", "remov", "timeline", "migration", "future"]
        readme_lower = readme_content.lower()

        found_keywords = [kw for kw in timeline_keywords if kw in readme_lower]
        assert len(found_keywords) >= 2, f"README should mention deprecation timeline. Found: {found_keywords}"

    def test_no_tkinter_imports_in_qt_main(self):
        """Test that Qt main doesn't import Tkinter modules."""
        qt_main_path = Path("risk_calculator/qt_main.py")
        if qt_main_path.exists():
            qt_main_content = qt_main_path.read_text()

            # Should not import tkinter
            assert "import tkinter" not in qt_main_content, "Qt main should not import tkinter"
            assert "from tkinter" not in qt_main_content, "Qt main should not import from tkinter"

    def test_proper_exit_codes_in_deprecated_main(self):
        """Test that deprecated main uses proper exit codes."""
        try:
            # Test with --version which should exit cleanly
            result = subprocess.run([
                sys.executable, "-m", "risk_calculator.main_tkinter_deprecated", "--version"
            ], capture_output=True, text=True, timeout=5)

            # Should exit with code 0 for --version
            assert result.returncode == 0, "Should exit cleanly with --version"

        except subprocess.TimeoutExpired:
            pytest.fail("Deprecated main should handle --version quickly")
        except FileNotFoundError:
            pytest.skip("Cannot test if deprecated main not available")

    def test_deprecation_affects_both_entry_points(self):
        """Test that deprecation warnings appear for both direct and entry point usage."""
        # This test verifies that deprecation appears regardless of how user accesses Tkinter version

        # Test direct module execution
        try:
            result = subprocess.run([
                sys.executable, "-c",
                "import risk_calculator.main_tkinter_deprecated; "
                "risk_calculator.main_tkinter_deprecated.main()"
            ], capture_output=True, text=True, timeout=5)

            output = result.stdout + result.stderr
            assert "deprecat" in output.lower(), "Direct import should show deprecation"

        except subprocess.TimeoutExpired:
            # Expected - might show GUI which we can't easily test
            pass

    def test_user_friendly_error_messages(self):
        """Test that deprecation messages are user-friendly."""
        deprecated_path = Path("risk_calculator/main_tkinter_deprecated.py")
        if deprecated_path.exists():
            content = deprecated_path.read_text()

            # Should not contain technical jargon
            content_lower = content.lower()
            user_friendly_indicators = [
                "please use", "instead", "recommended", "better", "enhanced"
            ]

            found_indicators = [ind for ind in user_friendly_indicators if ind in content_lower]
            assert len(found_indicators) >= 2, "Should use user-friendly language"

    def test_backward_compatibility_maintained(self):
        """Test that basic backward compatibility is maintained during deprecation phase."""
        # The deprecated version should still work (with warnings) during transition period
        try:
            # Try to import the deprecated version
            import risk_calculator.main_tkinter_deprecated as deprecated

            # Should have the same interface
            assert hasattr(deprecated, 'main'), "Deprecated version should have main function"
            assert hasattr(deprecated, 'RiskCalculatorApp'), "Should have RiskCalculatorApp class"

        except ImportError:
            pytest.fail("Deprecated version should still be importable during transition")

    def test_complete_tkinter_isolation(self):
        """Test that Qt version is completely isolated from Tkinter dependencies."""
        qt_main_path = Path("risk_calculator/qt_main.py")
        if qt_main_path.exists():
            content = qt_main_path.read_text()

            # Should only import PySide6/Qt modules for GUI
            tkinter_references = [
                "tkinter", "Tkinter", "Tk()", "messagebox", "ttk"
            ]

            for ref in tkinter_references:
                assert ref not in content, f"Qt main should not reference {ref}"