"""
Unit tests for FontManager class and font scaling functionality.
Tests all methods and edge cases for responsive font scaling system.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFontManager(unittest.TestCase):
    """Test FontManager class functionality."""

    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        self.style = ttk.Style()

        # Import here to avoid path issues
        from risk_calculator.views.main_window import FontManager
        self.font_manager = FontManager(self.style)

    def tearDown(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_calculate_scale_factor_normal_cases(self):
        """Test scale factor calculation for normal window heights."""
        # Test base height (600px) gives 1.0 scale
        scale = self.font_manager.calculate_scale_factor(600)
        self.assertAlmostEqual(scale, 1.0, places=2)

        # Test smaller height gives smaller scale
        scale = self.font_manager.calculate_scale_factor(480)  # 80% of base
        self.assertAlmostEqual(scale, 0.8, places=2)

        # Test larger height gives larger scale
        scale = self.font_manager.calculate_scale_factor(900)  # 150% of base
        self.assertAlmostEqual(scale, 1.5, places=2)

    def test_calculate_scale_factor_bounds(self):
        """Test scale factor bounds are respected."""
        # Test minimum bound (below min_height)
        scale = self.font_manager.calculate_scale_factor(300)  # Very small
        self.assertGreaterEqual(scale, self.font_manager.min_scale)

        # Test maximum bound (very large height)
        scale = self.font_manager.calculate_scale_factor(2000)  # Very large
        self.assertLessEqual(scale, self.font_manager.max_scale)

        # Specific boundary tests
        scale = self.font_manager.calculate_scale_factor(400)  # Below min_height
        self.assertAlmostEqual(scale, self.font_manager.min_scale, places=2)

        scale = self.font_manager.calculate_scale_factor(1500)  # Above max scale
        self.assertAlmostEqual(scale, self.font_manager.max_scale, places=2)

    def test_get_scaled_font_size_calculation(self):
        """Test scaled font size calculation."""
        # Test normal scaling
        size = self.font_manager.get_scaled_font_size(10, 1.5)
        self.assertEqual(size, 15)

        # Test fractional scaling (should round down)
        size = self.font_manager.get_scaled_font_size(10, 1.2)
        self.assertEqual(size, 12)

        # Test very small scale
        size = self.font_manager.get_scaled_font_size(10, 0.5)
        self.assertEqual(size, 8)  # Minimum bound

    def test_get_scaled_font_size_bounds(self):
        """Test font size bounds are enforced."""
        # Test minimum bound
        size = self.font_manager.get_scaled_font_size(6, 0.5)  # Would be 3
        self.assertEqual(size, 8)  # Minimum is 8

        # Test maximum bound
        size = self.font_manager.get_scaled_font_size(20, 2.0)  # Would be 40
        self.assertEqual(size, 24)  # Maximum is 24

        # Test normal case within bounds
        size = self.font_manager.get_scaled_font_size(12, 1.0)
        self.assertEqual(size, 12)

    def test_register_widget_for_font_scaling(self):
        """Test widget registration for font scaling."""
        # Create mock widget
        mock_widget = Mock()
        mock_widget.winfo_exists.return_value = True

        # Register widget
        self.font_manager.register_widget_for_font_scaling(mock_widget, 'label')

        # Verify widget was added to tracking
        self.assertEqual(len(self.font_manager.font_widgets), 1)
        self.assertEqual(self.font_manager.font_widgets[0], (mock_widget, 'label'))

    def test_cleanup_widgets_removes_destroyed(self):
        """Test cleanup removes destroyed widgets."""
        # Create mock widgets - one exists, one doesn't
        mock_widget1 = Mock()
        mock_widget1.winfo_exists.return_value = True
        mock_widget2 = Mock()
        mock_widget2.winfo_exists.return_value = False

        # Register both widgets
        self.font_manager.register_widget_for_font_scaling(mock_widget1, 'label')
        self.font_manager.register_widget_for_font_scaling(mock_widget2, 'entry')

        # Should have 2 widgets
        self.assertEqual(len(self.font_manager.font_widgets), 2)

        # Cleanup should remove destroyed widget
        self.font_manager.cleanup_widgets()

        # Should have 1 widget remaining
        self.assertEqual(len(self.font_manager.font_widgets), 1)
        self.assertEqual(self.font_manager.font_widgets[0], (mock_widget1, 'label'))

    @patch('tkinter.ttk.Style.configure')
    def test_update_ttk_styles(self, mock_configure):
        """Test TTK style updates with font scaling."""
        # Test style updates
        self.font_manager._update_ttk_styles(1.5)

        # Verify configure was called for each style
        expected_calls = [
            call('TLabel', font=('TkDefaultFont', 13)),      # 9 * 1.5 = 13.5 -> 13
            call('TEntry', font=('TkDefaultFont', 13)),       # 9 * 1.5 = 13.5 -> 13
            call('TButton', font=('TkDefaultFont', 13)),      # 9 * 1.5 = 13.5 -> 13
            call('Title.TLabel', font=('TkDefaultFont', 18, 'bold')),  # 12 * 1.5 = 18
            call('Error.TLabel', font=('TkDefaultFont', 12)), # 8 * 1.5 = 12
            call('Warning.TLabel', font=('TkDefaultFont', 12)),
            call('Success.TLabel', font=('TkDefaultFont', 12))
        ]

        mock_configure.assert_has_calls(expected_calls, any_order=True)

    def test_update_widget_fonts(self):
        """Test individual widget font updates."""
        # Create mock widgets with different types
        mock_label = Mock()
        mock_label.winfo_exists.return_value = True
        mock_label.configure = Mock()

        mock_entry = Mock()
        mock_entry.winfo_exists.return_value = True
        mock_entry.configure = Mock()

        # Register widgets
        self.font_manager.register_widget_for_font_scaling(mock_label, 'label')
        self.font_manager.register_widget_for_font_scaling(mock_entry, 'entry')

        # Update fonts
        self.font_manager._update_widget_fonts(1.5)

        # Verify widgets were configured with scaled fonts
        mock_label.configure.assert_called_once()
        mock_entry.configure.assert_called_once()

        # Check font arguments
        label_call_args = mock_label.configure.call_args[1]
        entry_call_args = mock_entry.configure.call_args[1]

        self.assertIn('font', label_call_args)
        self.assertIn('font', entry_call_args)

    def test_update_fonts_for_height_threshold(self):
        """Test font update threshold prevents excessive updates."""
        # Mock the update methods
        with patch.object(self.font_manager, '_update_ttk_styles') as mock_ttk_styles, \
             patch.object(self.font_manager, '_update_widget_fonts') as mock_widget_fonts:

            # First update should trigger
            self.font_manager.update_fonts_for_height(650)
            mock_ttk_styles.assert_called_once()
            mock_widget_fonts.assert_called_once()

            # Reset mocks
            mock_ttk_styles.reset_mock()
            mock_widget_fonts.reset_mock()

            # Small change should not trigger (within threshold)
            self.font_manager.update_fonts_for_height(655)  # Small change within 0.02 threshold
            mock_ttk_styles.assert_not_called()
            mock_widget_fonts.assert_not_called()

            # Large change should trigger
            self.font_manager.update_fonts_for_height(750)  # Large change
            mock_ttk_styles.assert_called_once()
            mock_widget_fonts.assert_called_once()

    def test_update_fonts_for_height_scale_tracking(self):
        """Test that current scale is properly tracked."""
        initial_scale = self.font_manager.current_scale

        # Update with different height
        self.font_manager.update_fonts_for_height(800)

        # Scale should have changed
        self.assertNotEqual(self.font_manager.current_scale, initial_scale)

        # Scale should match calculated value
        expected_scale = self.font_manager.calculate_scale_factor(800)
        self.assertAlmostEqual(self.font_manager.current_scale, expected_scale, places=2)

    def test_font_size_edge_cases(self):
        """Test edge cases for font size calculations."""
        # Zero scale (shouldn't happen but test robustness)
        size = self.font_manager.get_scaled_font_size(10, 0)
        self.assertEqual(size, 8)  # Minimum

        # Negative scale (shouldn't happen but test robustness)
        size = self.font_manager.get_scaled_font_size(10, -1)
        self.assertEqual(size, 8)  # Minimum

        # Very large scale
        size = self.font_manager.get_scaled_font_size(10, 10)
        self.assertEqual(size, 24)  # Maximum

    def test_different_window_sizes(self):
        """Test font scaling at different realistic window sizes."""
        test_cases = [
            (500, 0.83),   # Small window -> min scale
            (600, 1.0),    # Base window -> 1.0 scale
            (750, 1.25),   # Medium window -> 1.25 scale
            (900, 1.5),    # Large window -> 1.5 scale
            (1200, 2.0),   # Very large window -> 2.0 scale
            (1500, 2.5),   # Huge window -> max scale
        ]

        for height, expected_scale in test_cases:
            with self.subTest(height=height):
                scale = self.font_manager.calculate_scale_factor(height)
                self.assertAlmostEqual(scale, expected_scale, places=1)

    def test_widget_font_updates_with_exceptions(self):
        """Test widget font updates handle exceptions gracefully."""
        # Create mock widget that throws exception
        mock_widget = Mock()
        mock_widget.winfo_exists.return_value = True
        mock_widget.configure.side_effect = Exception("Widget error")

        # Register widget
        self.font_manager.register_widget_for_font_scaling(mock_widget, 'label')

        # Update should not crash even with widget exception
        try:
            self.font_manager._update_widget_fonts(1.5)
        except Exception:
            self.fail("_update_widget_fonts should handle widget exceptions gracefully")

    def test_base_font_sizes_configuration(self):
        """Test that base font sizes are properly configured."""
        expected_fonts = {
            'label': 9,
            'entry': 9,
            'button': 9,
            'error': 8,
            'info': 8,
            'result': 10,
            'title': 12
        }

        self.assertEqual(self.font_manager.base_fonts, expected_fonts)

    def test_font_manager_initialization(self):
        """Test FontManager initialization values."""
        self.assertEqual(self.font_manager.base_height, 600)
        self.assertEqual(self.font_manager.min_height, 500)
        self.assertEqual(self.font_manager.max_scale, 2.5)
        self.assertEqual(self.font_manager.min_scale, 0.8)
        self.assertEqual(self.font_manager.current_scale, 1.0)
        self.assertEqual(len(self.font_manager.font_widgets), 0)


if __name__ == '__main__':
    unittest.main()