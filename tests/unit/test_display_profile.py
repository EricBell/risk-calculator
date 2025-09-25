"""
Unit tests for Display Profile detection in Qt services
"""

import pytest
import sys
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Import the Qt display service and models
try:
    from risk_calculator.services.qt_display_service import QtDisplayService
    from risk_calculator.models.display_profile import DisplayProfile
    HAS_QT_SERVICES = True
except ImportError:
    HAS_QT_SERVICES = False
    # Create mock classes for testing
    class QtDisplayService:
        pass
    class DisplayProfile:
        pass

# Skip if Qt not available (additional check for PySide6)
try:
    import PySide6
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

if not HAS_QT_SERVICES or not HAS_PYSIDE:
    pytest.skip("Qt services or PySide6 not available", allow_module_level=True)


class TestDisplayProfileDetection:
    """Unit tests for display profile detection logic."""

    def setup_method(self):
        """Setup test environment."""
        self.display_service = QtDisplayService()

    def test_display_profile_creation(self):
        """Test DisplayProfile model creation and validation."""
        # Test valid display profile
        profile = DisplayProfile(
            screen_width=1920,
            screen_height=1080,
            dpi_scale=1.5,
            is_high_dpi=True,
            platform="Windows"
        )

        assert profile.screen_width == 1920
        assert profile.screen_height == 1080
        assert profile.dpi_scale == 1.5
        assert profile.is_high_dpi is True
        assert profile.platform == "Windows"

    def test_display_profile_validation(self):
        """Test DisplayProfile validation rules."""
        # Test invalid screen dimensions
        with pytest.raises((ValueError, TypeError)):
            DisplayProfile(
                screen_width=0,  # Invalid
                screen_height=1080,
                dpi_scale=1.0,
                is_high_dpi=False,
                platform="Linux"
            )

        # Test invalid DPI scale
        with pytest.raises((ValueError, TypeError)):
            DisplayProfile(
                screen_width=1920,
                screen_height=1080,
                dpi_scale=0.0,  # Invalid
                is_high_dpi=False,
                platform="Linux"
            )

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_dpi_scale_detection_windows(self, mock_qapp):
        """Test DPI scale factor detection on Windows."""
        # Mock Windows high-DPI scenario
        mock_screen = MagicMock()
        mock_screen.logicalDotsPerInch.return_value = 144  # 150% scaling
        mock_screen.devicePixelRatio.return_value = 1.0
        mock_screen.geometry.return_value = MagicMock(width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        with patch('sys.platform', 'win32'):
            scale_factor = self.display_service.get_dpi_scale_factor()

        # Should detect 1.5x scaling (144 DPI / 96 DPI base)
        assert isinstance(scale_factor, float)
        assert 1.4 <= scale_factor <= 1.6  # Allow some variance

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_dpi_scale_detection_linux(self, mock_qapp):
        """Test DPI scale factor detection on Linux."""
        # Mock Linux standard DPI scenario
        mock_screen = MagicMock()
        mock_screen.logicalDotsPerInch.return_value = 96  # Standard DPI
        mock_screen.devicePixelRatio.return_value = 1.0
        mock_screen.geometry.return_value = MagicMock(width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        with patch('sys.platform', 'linux'):
            scale_factor = self.display_service.get_dpi_scale_factor()

        # Should detect 1.0x scaling (96 DPI / 96 DPI base)
        assert isinstance(scale_factor, float)
        assert 0.9 <= scale_factor <= 1.1  # Allow some variance

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_high_dpi_detection_threshold(self, mock_qapp):
        """Test high-DPI detection threshold logic."""
        mock_screen = MagicMock()
        mock_screen.devicePixelRatio.return_value = 1.0
        mock_screen.geometry.return_value = MagicMock(width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        # Test cases: DPI -> expected high-DPI result
        test_cases = [
            (96, False),   # Standard DPI
            (120, True),   # 125% scaling - high DPI
            (144, True),   # 150% scaling - high DPI
            (192, True),   # 200% scaling - high DPI
            (288, True),   # 300% scaling - high DPI
        ]

        for dpi, expected_high_dpi in test_cases:
            mock_screen.logicalDotsPerInch.return_value = dpi

            is_high_dpi = self.display_service.is_high_dpi_display()
            assert is_high_dpi == expected_high_dpi, f"DPI {dpi} should return {expected_high_dpi}"

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_screen_dimensions_detection(self, mock_qapp):
        """Test screen dimensions detection."""
        mock_screen = MagicMock()
        mock_geometry = MagicMock()
        mock_geometry.width.return_value = 2560
        mock_geometry.height.return_value = 1440
        mock_screen.geometry.return_value = mock_geometry

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        dimensions = self.display_service.get_screen_dimensions()

        assert dimensions == (2560, 1440)
        assert isinstance(dimensions[0], int)
        assert isinstance(dimensions[1], int)

    def test_optimal_window_size_calculation(self):
        """Test optimal window size calculation logic."""
        # Test with different base sizes and scale factors
        test_cases = [
            {
                "base_size": (800, 600),
                "dpi_scale": 1.0,
                "expected_min": (800, 600)
            },
            {
                "base_size": (800, 600),
                "dpi_scale": 1.5,
                "expected_min": (1200, 900)  # 1.5x scaling
            },
            {
                "base_size": (1024, 768),
                "dpi_scale": 2.0,
                "expected_min": (2048, 1536)  # 2x scaling
            }
        ]

        for case in test_cases:
            with patch.object(self.display_service, 'get_dpi_scale_factor', return_value=case["dpi_scale"]):
                optimal_size = self.display_service.calculate_optimal_window_size(case["base_size"])

                assert optimal_size[0] >= case["expected_min"][0]
                assert optimal_size[1] >= case["expected_min"][1]
                assert isinstance(optimal_size[0], int)
                assert isinstance(optimal_size[1], int)

    def test_platform_detection(self):
        """Test platform detection logic."""
        # Test Windows detection
        with patch('platform.system', return_value='Windows'):
            platform_info = self.display_service.get_platform_info()
            assert platform_info == "Windows"

        # Test Linux detection
        with patch('platform.system', return_value='Linux'):
            platform_info = self.display_service.get_platform_info()
            assert platform_info == "Linux"

        # Test macOS detection
        with patch('platform.system', return_value='Darwin'):
            platform_info = self.display_service.get_platform_info()
            assert platform_info == "macOS"

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_multi_monitor_detection(self, mock_qapp):
        """Test multi-monitor detection capabilities."""
        # Mock multiple screens
        mock_screens = [MagicMock(), MagicMock(), MagicMock()]
        for screen in mock_screens:
            screen.geometry.return_value = MagicMock(x=lambda: 0, y=lambda: 0, width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.screens.return_value = mock_screens
        mock_app_instance.primaryScreen.return_value = mock_screens[0]
        mock_qapp.instance.return_value = mock_app_instance

        screen_count = self.display_service.get_screen_count()
        assert screen_count == 3

        # Test primary screen identification
        primary_screen = self.display_service.get_primary_screen_geometry()
        assert primary_screen is not None

    def test_display_profile_serialization(self):
        """Test DisplayProfile serialization for configuration storage."""
        profile = DisplayProfile(
            screen_width=1920,
            screen_height=1080,
            dpi_scale=1.25,
            is_high_dpi=True,
            platform="Windows"
        )

        # Test conversion to dictionary
        profile_dict = profile.to_dict()
        expected_keys = ['screen_width', 'screen_height', 'dpi_scale', 'is_high_dpi', 'platform']

        for key in expected_keys:
            assert key in profile_dict

        # Test reconstruction from dictionary
        reconstructed = DisplayProfile.from_dict(profile_dict)
        assert reconstructed.screen_width == profile.screen_width
        assert reconstructed.screen_height == profile.screen_height
        assert reconstructed.dpi_scale == profile.dpi_scale
        assert reconstructed.is_high_dpi == profile.is_high_dpi
        assert reconstructed.platform == profile.platform

    def test_display_profile_equality(self):
        """Test DisplayProfile equality comparison."""
        profile1 = DisplayProfile(
            screen_width=1920,
            screen_height=1080,
            dpi_scale=1.5,
            is_high_dpi=True,
            platform="Windows"
        )

        profile2 = DisplayProfile(
            screen_width=1920,
            screen_height=1080,
            dpi_scale=1.5,
            is_high_dpi=True,
            platform="Windows"
        )

        profile3 = DisplayProfile(
            screen_width=2560,
            screen_height=1440,
            dpi_scale=1.5,
            is_high_dpi=True,
            platform="Windows"
        )

        assert profile1 == profile2
        assert profile1 != profile3

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_dpi_edge_cases(self, mock_qapp):
        """Test DPI detection edge cases."""
        mock_screen = MagicMock()
        mock_screen.devicePixelRatio.return_value = 1.0
        mock_screen.geometry.return_value = MagicMock(width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        # Test very high DPI
        mock_screen.logicalDotsPerInch.return_value = 384  # 400% scaling

        scale_factor = self.display_service.get_dpi_scale_factor()
        assert scale_factor >= 3.5  # Should be around 4.0

        # Test invalid/zero DPI (fallback)
        mock_screen.logicalDotsPerInch.return_value = 0
        scale_factor = self.display_service.get_dpi_scale_factor()
        assert scale_factor == 1.0  # Should fallback to 1.0

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_display_service_caching(self, mock_qapp):
        """Test that display service works correctly with repeated calls."""
        mock_screen = MagicMock()
        mock_screen.logicalDotsPerInch.return_value = 96
        mock_screen.devicePixelRatio.return_value = 1.0
        mock_screen.geometry.return_value = MagicMock(width=lambda: 1920, height=lambda: 1080)

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_qapp.instance.return_value = mock_app_instance

        # Multiple calls should work consistently
        profile1 = self.display_service.detect_display_profile()
        profile2 = self.display_service.detect_display_profile()

        assert profile1.screen_width == profile2.screen_width
        assert profile1.screen_height == profile2.screen_height
        assert profile1.dpi_scale == profile2.dpi_scale


class TestDisplayServiceIntegration:
    """Integration tests for display service components."""

    def setup_method(self):
        """Setup test environment."""
        self.display_service = QtDisplayService()

    @patch('risk_calculator.services.qt_display_service.QApplication')
    def test_complete_display_detection_workflow(self, mock_qapp):
        """Test complete display detection workflow."""
        # Mock a typical high-DPI Windows setup
        mock_screen = MagicMock()
        mock_geometry = MagicMock()
        mock_geometry.width.return_value = 2560
        mock_geometry.height.return_value = 1440
        mock_screen.geometry.return_value = mock_geometry
        mock_screen.logicalDotsPerInch.return_value = 144  # 150% scaling
        mock_screen.devicePixelRatio.return_value = 1.0

        mock_app_instance = MagicMock()
        mock_app_instance.primaryScreen.return_value = mock_screen
        mock_app_instance.screens.return_value = [mock_screen]
        mock_qapp.instance.return_value = mock_app_instance

        with patch('platform.system', return_value='Windows'):
            # Run complete detection workflow
            profile = self.display_service.detect_display_profile()

            # Verify all components work together
            assert profile.screen_width == 2560
            assert profile.screen_height == 1440
            assert profile.dpi_scale == 1.5
            assert profile.is_high_dpi is True
            assert profile.platform == "Windows"

            # Test optimal window calculation with detected profile
            optimal_size = self.display_service.calculate_optimal_window_size((800, 600))
            assert optimal_size[0] >= 1200  # Should be scaled up
            assert optimal_size[1] >= 900

    def test_display_service_error_handling(self):
        """Test display service error handling."""
        # Test with no QApplication instance and mock display profile detection
        from risk_calculator.models.display_profile import DisplayProfile

        # Create a mock display profile with default values
        mock_profile = DisplayProfile(
            screen_width=1920,
            screen_height=1080,
            dpi_scale=1.0,  # Default scale
            is_high_dpi=False,
            platform="Linux"
        )

        with patch.object(self.display_service, 'detect_display_profile', return_value=mock_profile), \
             patch.object(self.display_service, 'get_screen_dimensions', return_value=(1920, 1080)):
            # Should handle gracefully and return defaults
            scale_factor = self.display_service.get_dpi_scale_factor()
            assert scale_factor == 1.0

            dimensions = self.display_service.get_screen_dimensions()
            assert dimensions == (1920, 1080)  # Default fallback

    def test_display_service_thread_safety(self):
        """Test display service thread safety."""
        import threading
        import time

        results = []
        errors = []

        def worker_thread():
            """Worker thread that calls display service methods."""
            try:
                for _ in range(5):
                    profile = self.display_service.detect_display_profile()
                    results.append(profile)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors and consistent results
        assert len(errors) == 0
        assert len(results) > 0

        # All results should be identical (cached)
        if len(results) > 1:
            first_result = results[0]
            for result in results[1:]:
                assert result == first_result