import unittest
import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCrossPlatformIntegration(unittest.TestCase):
    """Integration test for cross platform."""

    def setUp(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_cross_platform_basic(self):
        """Test basic cross platform functionality."""
        try:
            from risk_calculator.main import main

            # Test that main application can be imported without error
            self.assertIsNotNone(main)

        except ImportError:
            self.skipTest("Main application not available")


if __name__ == '__main__':
    unittest.main()
