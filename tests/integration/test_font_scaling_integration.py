"""
Integration tests for font scaling during window resize.
Tests the complete font scaling system working with real UI components.
"""

import unittest
from unittest.mock import Mock, patch
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestFontScalingIntegration(unittest.TestCase):
    """Integration tests for font scaling system."""

    def setUp(self):
        """Setup test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests

    def tearDown(self):
        """Cleanup test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_font_scaling_with_real_widgets(self):
        """Test font scaling with actual Tkinter widgets."""
        try:
            from risk_calculator.views.main_window import FontManager

            # Create FontManager with real TTK style
            style = ttk.Style()
            font_manager = FontManager(style)

            # Create test widgets
            label = ttk.Label(self.root, text="Test Label")
            entry = ttk.Entry(self.root)
            button = ttk.Button(self.root, text="Test Button")

            # Register widgets
            font_manager.register_widget_for_font_scaling(label, 'label')
            font_manager.register_widget_for_font_scaling(entry, 'entry')
            font_manager.register_widget_for_font_scaling(button, 'button')

            # Test different window heights
            test_heights = [500, 600, 750, 900, 1200]
            previous_scale = None

            for height in test_heights:
                font_manager.update_fonts_for_height(height)
                current_scale = font_manager.current_scale

                # Verify scale changes appropriately
                expected_scale = font_manager.calculate_scale_factor(height)
                self.assertAlmostEqual(current_scale, expected_scale, places=2)

                # Verify scale increases with height (except for bounds)
                if previous_scale is not None and height > 600:
                    if expected_scale < font_manager.max_scale:
                        self.assertGreaterEqual(current_scale, previous_scale)

                previous_scale = current_scale

        except ImportError:
            self.skipTest("FontManager not available")

    def test_widget_registration_during_tab_creation(self):
        """Test that widgets are properly registered when tabs are created."""
        try:
            from risk_calculator.views.equity_tab import EquityTab
            from risk_calculator.views.main_window import MainWindow

            # Create main window and tab
            main_window = MainWindow(self.root)
            equity_tab = EquityTab(main_window.notebook)

            # Set main window reference for tab
            equity_tab.main_window = main_window

            # Trigger widget registration
            equity_tab._register_widgets_for_font_scaling()

            # Verify that widgets were registered
            # The font manager should have widgets registered
            self.assertGreater(len(main_window.font_manager.font_widgets), 0)

        except ImportError:
            self.skipTest("Tab components not available")

    def test_main_window_font_scaling_integration(self):
        """Test MainWindow font scaling integration."""
        try:
            from risk_calculator.views.main_window import MainWindow

            # Create main window
            main_window = MainWindow(self.root)

            # Get initial font manager state
            initial_scale = main_window.font_manager.current_scale

            # Simulate window resize by calling the update method directly
            main_window.font_manager.update_fonts_for_height(800)

            # Verify scale changed
            new_scale = main_window.font_manager.current_scale
            self.assertNotEqual(initial_scale, new_scale)

            # Verify scale is appropriate for 800px height
            expected_scale = main_window.font_manager.calculate_scale_factor(800)
            self.assertAlmostEqual(new_scale, expected_scale, places=2)

        except ImportError:
            self.skipTest("MainWindow not available")

    def test_font_scaling_with_controller_integration(self):
        """Test font scaling works with EnhancedMainController."""
        try:
            from risk_calculator.views.main_window import MainWindow
            from risk_calculator.controllers.enhanced_main_controller import EnhancedMainController

            # Create main window and controller
            main_window = MainWindow(self.root)
            controller = EnhancedMainController(main_window)

            # Verify controller has notification method
            self.assertTrue(hasattr(controller, 'notify_window_resize'))

            # Test notification method doesn't crash
            try:
                controller.notify_window_resize(800, 600)
            except Exception as e:
                self.fail(f"Controller notification failed: {e}")

        except ImportError:
            self.skipTest("Controller integration not available")

    def test_font_sizes_at_different_scales(self):
        """Test that font sizes are calculated correctly at different scales."""
        try:
            from risk_calculator.views.main_window import FontManager

            style = ttk.Style()
            font_manager = FontManager(style)

            # Test specific scale factors and expected font sizes
            test_cases = [
                (0.8, 'label', 9, 8),    # 9 * 0.8 = 7.2 -> 8 (min bound)
                (1.0, 'label', 9, 9),    # 9 * 1.0 = 9
                (1.5, 'entry', 9, 13),   # 9 * 1.5 = 13.5 -> 13
                (2.0, 'button', 9, 18),  # 9 * 2.0 = 18
                (2.5, 'title', 12, 24),  # 12 * 2.5 = 30 -> 24 (max bound)
            ]

            for scale, font_type, base_size, expected_size in test_cases:
                with self.subTest(scale=scale, font_type=font_type):
                    calculated_size = font_manager.get_scaled_font_size(base_size, scale)
                    self.assertEqual(calculated_size, expected_size)

        except ImportError:
            self.skipTest("FontManager not available")

    def test_widget_cleanup_removes_destroyed_widgets(self):
        """Test that widget cleanup properly removes destroyed widgets."""
        try:
            from risk_calculator.views.main_window import FontManager

            style = ttk.Style()
            font_manager = FontManager(style)

            # Create and register widgets
            label1 = ttk.Label(self.root, text="Label 1")
            label2 = ttk.Label(self.root, text="Label 2")

            font_manager.register_widget_for_font_scaling(label1, 'label')
            font_manager.register_widget_for_font_scaling(label2, 'label')

            # Verify both widgets are registered
            self.assertEqual(len(font_manager.font_widgets), 2)

            # Destroy one widget
            label1.destroy()

            # Cleanup should remove destroyed widget
            font_manager.cleanup_widgets()

            # Should have one widget remaining
            self.assertEqual(len(font_manager.font_widgets), 1)
            self.assertEqual(font_manager.font_widgets[0][0], label2)

        except ImportError:
            self.skipTest("FontManager not available")

    def test_responsive_threshold_behavior(self):
        """Test that the responsive threshold prevents excessive updates."""
        try:
            from risk_calculator.views.main_window import FontManager

            style = ttk.Style()
            font_manager = FontManager(style)

            # Mock the update methods to track calls
            with patch.object(font_manager, '_update_ttk_styles') as mock_ttk, \
                 patch.object(font_manager, '_update_widget_fonts') as mock_widgets:

                # Initial update should trigger
                font_manager.update_fonts_for_height(650)
                self.assertEqual(mock_ttk.call_count, 1)
                self.assertEqual(mock_widgets.call_count, 1)

                # Small change (within threshold) should not trigger
                mock_ttk.reset_mock()
                mock_widgets.reset_mock()
                font_manager.update_fonts_for_height(655)  # Small change
                self.assertEqual(mock_ttk.call_count, 0)
                self.assertEqual(mock_widgets.call_count, 0)

                # Large change should trigger
                font_manager.update_fonts_for_height(700)  # Large change
                self.assertEqual(mock_ttk.call_count, 1)
                self.assertEqual(mock_widgets.call_count, 1)

        except ImportError:
            self.skipTest("FontManager not available")

    def test_comprehensive_window_size_scaling(self):
        """Test font scaling across comprehensive range of window sizes."""
        try:
            from risk_calculator.views.main_window import FontManager

            style = ttk.Style()
            font_manager = FontManager(style)

            # Test realistic window sizes for laptop/desktop usage
            window_sizes = [
                (500, 0.83),   # Small window
                (600, 1.0),    # Base size
                (720, 1.2),    # HD height
                (900, 1.5),    # Large window
                (1080, 1.8),   # Full HD height
                (1200, 2.0),   # Large desktop
                (1440, 2.4),   # High DPI
                (1600, 2.5),   # Max scale (bounded)
            ]

            for height, expected_scale in window_sizes:
                with self.subTest(height=height):
                    scale = font_manager.calculate_scale_factor(height)

                    # Verify scale is within expected range
                    self.assertAlmostEqual(scale, expected_scale, places=1)

                    # Verify scale is within bounds
                    self.assertGreaterEqual(scale, font_manager.min_scale)
                    self.assertLessEqual(scale, font_manager.max_scale)

        except ImportError:
            self.skipTest("FontManager not available")


if __name__ == '__main__':
    unittest.main()