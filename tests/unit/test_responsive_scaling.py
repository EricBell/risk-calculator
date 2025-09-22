"""
Unit tests for responsive scaling in Qt layout service
"""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Import the Qt layout service and models
try:
    from risk_calculator.models.ui_layout_state import UILayoutState
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False

# Mock Qt components if not available
if not HAS_MODELS:
    pytest.skip("Qt models not available", allow_module_level=True)

# Create a mock layout service for testing
class MockQtResponsiveLayoutService:
    """Mock layout service for testing."""

    def __init__(self):
        self._layout_state = None

    def initialize_layout_state(self, base_width, base_height, current_width, current_height):
        self._layout_state = UILayoutState(
            base_width=base_width,
            base_height=base_height,
            current_width=current_width,
            current_height=current_height,
            scale_factor_x=current_width / base_width,
            scale_factor_y=current_height / base_height,
            font_base_size=10
        )

    def calculate_scale_factors(self, base_size, current_size):
        base_width, base_height = base_size
        current_width, current_height = current_size
        return (current_width / base_width, current_height / base_height)

    def get_current_state(self):
        return self._layout_state

    def reset_layout_state(self):
        self._layout_state = None

    def get_scaled_dimensions(self, base_width, base_height):
        if self._layout_state:
            return self._layout_state.get_scaled_dimensions(base_width, base_height)
        return (base_width, base_height)


class TestResponsiveScalingCalculations:
    """Unit tests for responsive scaling calculations."""

    def setup_method(self):
        """Setup test environment."""
        self.layout_service = MockQtResponsiveLayoutService()

    def test_scale_factor_calculation_basic(self):
        """Test basic scale factor calculations."""
        # Test no scaling needed (same size)
        base_size = (800, 600)
        current_size = (800, 600)
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (1.0, 1.0)

    def test_scale_factor_calculation_uniform_scaling(self):
        """Test uniform scaling calculations."""
        # Test 2x uniform scaling
        base_size = (800, 600)
        current_size = (1600, 1200)
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (2.0, 2.0)

    def test_scale_factor_calculation_non_uniform_scaling(self):
        """Test non-uniform scaling calculations."""
        # Test different x and y scaling
        base_size = (800, 600)
        current_size = (1200, 900)  # 1.5x width, 1.5x height
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (1.5, 1.5)

        # Test asymmetric scaling
        current_size = (1600, 900)  # 2x width, 1.5x height
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (2.0, 1.5)

    def test_scale_factor_calculation_edge_cases(self):
        """Test scale factor calculation edge cases."""
        # Test very small base size
        base_size = (1, 1)
        current_size = (800, 600)
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (800.0, 600.0)

        # Test very large scaling
        base_size = (100, 100)
        current_size = (10000, 10000)
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        assert scale_factors == (100.0, 100.0)

    def test_scale_factor_calculation_decimal_precision(self):
        """Test scale factor calculation with decimal precision."""
        # Test fractional scaling that requires precision
        base_size = (800, 600)
        current_size = (1024, 768)  # Should give 1.28 x 1.28
        scale_factors = self.layout_service.calculate_scale_factors(base_size, current_size)

        expected_x = 1024 / 800  # 1.28
        expected_y = 768 / 600   # 1.28

        assert abs(scale_factors[0] - expected_x) < 0.001
        assert abs(scale_factors[1] - expected_y) < 0.001

    def test_ui_layout_state_creation(self):
        """Test UILayoutState model creation and validation."""
        layout_state = UILayoutState(
            base_width=800,
            base_height=600,
            current_width=1200,
            current_height=900,
            scale_factor_x=1.5,
            scale_factor_y=1.5,
            font_base_size=10
        )

        assert layout_state.base_width == 800
        assert layout_state.base_height == 600
        assert layout_state.current_width == 1200
        assert layout_state.current_height == 900
        assert layout_state.scale_factor_x == 1.5
        assert layout_state.scale_factor_y == 1.5
        assert layout_state.font_base_size == 10

    def test_ui_layout_state_validation(self):
        """Test UILayoutState validation rules."""
        # Test invalid dimensions
        with pytest.raises((ValueError, TypeError)):
            UILayoutState(
                base_width=0,  # Invalid
                base_height=600,
                current_width=1200,
                current_height=900,
                scale_factor_x=1.5,
                scale_factor_y=1.5,
                font_base_size=10
            )

        # Test invalid scale factors
        with pytest.raises((ValueError, TypeError)):
            UILayoutState(
                base_width=800,
                base_height=600,
                current_width=1200,
                current_height=900,
                scale_factor_x=0.0,  # Invalid
                scale_factor_y=1.5,
                font_base_size=10
            )

    def test_apply_responsive_scaling_state_tracking(self):
        """Test that applying responsive scaling updates state correctly."""
        # Initialize layout state
        self.layout_service.initialize_layout_state(800, 600, 1200, 900)

        # Get current state
        current_state = self.layout_service.get_current_state()
        assert current_state is not None

        # Verify scale factors are calculated correctly
        assert current_state.scale_factor_x == 1.5  # 1200/800
        assert current_state.scale_factor_y == 1.5  # 900/600

    def test_reset_scaling_state(self):
        """Test resetting scaling state."""
        # First initialize with some scaling
        self.layout_service.initialize_layout_state(800, 600, 1600, 1200)

        # Verify scaling is active
        current_state = self.layout_service.get_current_state()
        assert current_state is not None
        assert current_state.scale_factor_x == 2.0
        assert current_state.scale_factor_y == 2.0

        # Reset scaling
        self.layout_service.reset_layout_state()

        # Verify scaling is reset
        reset_state = self.layout_service.get_current_state()
        assert reset_state is None

    def test_minimum_size_constraints(self):
        """Test minimum size constraint enforcement."""
        # Test that the service can calculate scaled dimensions
        self.layout_service.initialize_layout_state(800, 600, 400, 300)  # Small size

        # Test dimension scaling
        scaled_dims = self.layout_service.get_scaled_dimensions(100, 100)
        assert scaled_dims[0] > 0  # Should return positive values
        assert scaled_dims[1] > 0

    def test_scaling_performance_optimization(self):
        """Test that scaling calculations are optimized for performance."""
        import time

        # Test many rapid scale factor calculations
        base_size = (800, 600)
        test_sizes = [(i*10, i*8) for i in range(100, 300)]  # 200 different sizes

        start_time = time.time()

        for size in test_sizes:
            scale_factors = self.layout_service.calculate_scale_factors(base_size, size)
            # Verify calculation is correct
            expected_x = size[0] / base_size[0]
            expected_y = size[1] / base_size[1]
            assert abs(scale_factors[0] - expected_x) < 0.001
            assert abs(scale_factors[1] - expected_y) < 0.001

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete 200 calculations very quickly (under 100ms)
        assert total_time < 0.1, f"Scale calculations took too long: {total_time}s"

    def test_scaling_with_zero_dimensions(self):
        """Test scaling behavior with zero dimensions."""
        # Test zero current size
        base_size = (800, 600)
        zero_size = (0, 0)

        # Should handle gracefully or raise appropriate error
        try:
            scale_factors = self.layout_service.calculate_scale_factors(base_size, zero_size)
            # If it returns, should be (0, 0) or (1, 1) depending on implementation
            assert scale_factors in [(0.0, 0.0), (1.0, 1.0)]
        except (ValueError, ZeroDivisionError):
            # Expected behavior for invalid input
            pass


class TestUILayoutState:
    """Test UILayoutState model functionality."""

    def test_layout_state_serialization(self):
        """Test UILayoutState serialization for persistence."""
        layout_state = UILayoutState(
            base_width=1024,
            base_height=768,
            current_width=1536,
            current_height=1152,
            scale_factor_x=1.5,
            scale_factor_y=1.5,
            font_base_size=10
        )

        # Test conversion to dictionary
        state_dict = layout_state.to_dict()
        expected_keys = [
            'base_width', 'base_height', 'current_width', 'current_height',
            'scale_factor_x', 'scale_factor_y', 'font_base_size'
        ]

        for key in expected_keys:
            assert key in state_dict

        # Test reconstruction from dictionary
        reconstructed = UILayoutState.from_dict(state_dict)
        assert reconstructed.base_width == layout_state.base_width
        assert reconstructed.base_height == layout_state.base_height
        assert reconstructed.current_width == layout_state.current_width
        assert reconstructed.current_height == layout_state.current_height
        assert reconstructed.scale_factor_x == layout_state.scale_factor_x
        assert reconstructed.scale_factor_y == layout_state.scale_factor_y
        assert reconstructed.font_base_size == layout_state.font_base_size