"""
Unit tests for responsive scaling in Qt layout service
"""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

# Import the Qt layout service and models
try:
    from risk_calculator.services.qt_layout_service import QtLayoutService
    from risk_calculator.models.ui_layout_state import UILayoutState
    HAS_QT_SERVICES = True
except ImportError:
    HAS_QT_SERVICES = False

# Mock Qt components if not available
if not HAS_QT_SERVICES:
    pytest.skip("Qt layout services not available", allow_module_level=True)


class TestResponsiveScalingCalculations:
    """Unit tests for responsive scaling calculations."""

    def setup_method(self):
        """Setup test environment."""
        self.layout_service = QtLayoutService()

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
            scale_x=1.5,
            scale_y=1.5,
            is_scaling_active=True
        )

        assert layout_state.base_width == 800
        assert layout_state.base_height == 600
        assert layout_state.current_width == 1200
        assert layout_state.current_height == 900
        assert layout_state.scale_x == 1.5
        assert layout_state.scale_y == 1.5
        assert layout_state.is_scaling_active is True

    def test_ui_layout_state_validation(self):
        """Test UILayoutState validation rules."""
        # Test invalid dimensions
        with pytest.raises((ValueError, TypeError)):
            UILayoutState(
                base_width=0,  # Invalid
                base_height=600,
                current_width=1200,
                current_height=900,
                scale_x=1.5,
                scale_y=1.5,
                is_scaling_active=True
            )

        # Test invalid scale factors
        with pytest.raises((ValueError, TypeError)):
            UILayoutState(
                base_width=800,
                base_height=600,
                current_width=1200,
                current_height=900,
                scale_x=0.0,  # Invalid
                scale_y=1.5,
                is_scaling_active=True
            )

    def test_apply_responsive_scaling_state_tracking(self):
        """Test that applying responsive scaling updates state correctly."""
        scale_factors = (1.5, 1.2)

        # Apply scaling
        self.layout_service.apply_responsive_scaling(scale_factors)

        # Verify state is tracked
        current_scales = self.layout_service.get_current_scale_factors()
        assert current_scales == scale_factors

        # Verify scaling is marked as active
        assert self.layout_service.is_scaling_active() is True

    def test_reset_scaling_state(self):
        """Test resetting scaling state."""
        # First apply some scaling
        scale_factors = (2.0, 1.5)
        self.layout_service.apply_responsive_scaling(scale_factors)

        # Verify scaling is active
        assert self.layout_service.is_scaling_active() is True

        # Reset scaling
        self.layout_service.reset_scaling()

        # Verify scaling is reset
        current_scales = self.layout_service.get_current_scale_factors()
        assert current_scales == (1.0, 1.0)
        assert self.layout_service.is_scaling_active() is False

    def test_minimum_size_constraints(self):
        """Test minimum size constraint enforcement."""
        # Set minimum size
        min_width, min_height = 800, 600
        self.layout_service.set_minimum_size(min_width, min_height)

        # Test calculation that would result in size below minimum
        base_size = (1600, 1200)  # Large base
        current_size = (400, 300)  # Very small current (below minimum)

        # The service should enforce minimums in actual UI
        # This test verifies the minimum is stored correctly
        stored_min = self.layout_service.get_minimum_size()
        assert stored_min == (min_width, min_height)

    def test_scaling_with_constraints(self):
        """Test scaling calculations with constraints applied."""
        # Set up constraints
        self.layout_service.set_minimum_size(800, 600)

        # Test scaling that respects constraints
        base_size = (800, 600)
        target_size = (1200, 900)  # Valid size above minimum

        scale_factors = self.layout_service.calculate_scale_factors(base_size, target_size)
        assert scale_factors == (1.5, 1.5)

        # Apply scaling
        self.layout_service.apply_responsive_scaling(scale_factors)

        # Verify constraints are maintained
        current_layout = self.layout_service.get_current_layout_state()
        assert current_layout.current_width >= 800
        assert current_layout.current_height >= 600

    def test_layout_state_serialization(self):
        """Test UILayoutState serialization for persistence."""
        layout_state = UILayoutState(
            base_width=1024,
            base_height=768,
            current_width=1536,
            current_height=1152,
            scale_x=1.5,
            scale_y=1.5,
            is_scaling_active=True
        )

        # Test conversion to dictionary
        state_dict = layout_state.to_dict()
        expected_keys = [
            'base_width', 'base_height', 'current_width', 'current_height',
            'scale_x', 'scale_y', 'is_scaling_active'
        ]

        for key in expected_keys:
            assert key in state_dict

        # Test reconstruction from dictionary
        reconstructed = UILayoutState.from_dict(state_dict)
        assert reconstructed.base_width == layout_state.base_width
        assert reconstructed.base_height == layout_state.base_height
        assert reconstructed.current_width == layout_state.current_width
        assert reconstructed.current_height == layout_state.current_height
        assert reconstructed.scale_x == layout_state.scale_x
        assert reconstructed.scale_y == layout_state.scale_y
        assert reconstructed.is_scaling_active == layout_state.is_scaling_active

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

    def test_scaling_state_consistency(self):
        """Test that scaling state remains consistent across operations."""
        # Perform sequence of scaling operations
        operations = [
            (1.2, 1.2),
            (1.5, 1.3),
            (2.0, 1.8),
            (1.0, 1.0),  # Reset
            (1.25, 1.25)
        ]

        for scale_x, scale_y in operations:
            self.layout_service.apply_responsive_scaling((scale_x, scale_y))

            # Verify state consistency
            current_scales = self.layout_service.get_current_scale_factors()
            assert current_scales == (scale_x, scale_y)

            is_active = self.layout_service.is_scaling_active()
            expected_active = scale_x != 1.0 or scale_y != 1.0
            assert is_active == expected_active

    def test_concurrent_scaling_operations(self):
        """Test thread safety of scaling operations."""
        import threading
        import time

        results = []
        errors = []

        def scaling_worker(thread_id):
            """Worker that performs scaling operations."""
            try:
                for i in range(10):
                    scale = 1.0 + (thread_id * 0.1) + (i * 0.01)
                    self.layout_service.apply_responsive_scaling((scale, scale))

                    current = self.layout_service.get_current_scale_factors()
                    results.append((thread_id, i, current))
                    time.sleep(0.001)
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=scaling_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5.0)

        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent scaling errors: {errors}"

        # Verify operations completed
        assert len(results) > 0


class TestResponsiveLayoutIntegration:
    """Integration tests for responsive layout system."""

    def setup_method(self):
        """Setup test environment."""
        self.layout_service = QtLayoutService()

    def test_complete_responsive_workflow(self):
        """Test complete responsive layout workflow."""
        # 1. Initialize with base size
        base_size = (1024, 768)
        self.layout_service.set_base_size(base_size)

        # 2. Set minimum constraints
        self.layout_service.set_minimum_size(800, 600)

        # 3. Calculate scaling for new size
        new_size = (1536, 1152)  # 1.5x scaling
        scale_factors = self.layout_service.calculate_scale_factors(base_size, new_size)

        # 4. Apply responsive scaling
        self.layout_service.apply_responsive_scaling(scale_factors)

        # 5. Verify complete state
        current_state = self.layout_service.get_current_layout_state()
        assert current_state.base_width == 1024
        assert current_state.base_height == 768
        assert current_state.current_width == 1536
        assert current_state.current_height == 1152
        assert current_state.scale_x == 1.5
        assert current_state.scale_y == 1.5
        assert current_state.is_scaling_active is True

        # 6. Test reset workflow
        self.layout_service.reset_scaling()
        assert not self.layout_service.is_scaling_active()

    def test_layout_service_error_recovery(self):
        """Test layout service error recovery."""
        # Test with invalid scale factors
        invalid_scales = [
            (-1.0, 1.0),  # Negative scale
            (float('inf'), 1.0),  # Infinite scale
            (float('nan'), 1.0),  # NaN scale
        ]

        for invalid_scale in invalid_scales:
            try:
                self.layout_service.apply_responsive_scaling(invalid_scale)
                # If it doesn't raise an error, should have safe fallback
                current_scales = self.layout_service.get_current_scale_factors()
                assert all(0 < scale < 10 for scale in current_scales)  # Reasonable range
            except (ValueError, TypeError):
                # Expected behavior for invalid input
                pass

    def test_layout_persistence_workflow(self):
        """Test layout state persistence workflow."""
        # Apply some scaling
        self.layout_service.apply_responsive_scaling((1.25, 1.25))

        # Get current state
        current_state = self.layout_service.get_current_layout_state()

        # Simulate saving and loading state
        state_dict = current_state.to_dict()

        # Create new service instance (simulating app restart)
        new_layout_service = QtLayoutService()

        # Restore state
        restored_state = UILayoutState.from_dict(state_dict)
        new_layout_service.restore_layout_state(restored_state)

        # Verify state was restored correctly
        restored_current = new_layout_service.get_current_scale_factors()
        assert restored_current == (1.25, 1.25)
        assert new_layout_service.is_scaling_active() is True