"""
Performance tests for validation response time.
Tests that form validation completes in <50ms as per requirements.
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestValidationPerformance:
    """Performance tests for validation response time requirements."""

    @classmethod
    def setup_class(cls):
        """Setup Qt application for testing."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setup_method(self):
        """Setup test method with validation services."""
        try:
            from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
            from risk_calculator.services.realtime_validator import RealtimeValidator
            from risk_calculator.services.enhanced_form_validation_service import EnhancedFormValidationService

            self.validation_service = EnhancedValidationService()
            self.realtime_validator = RealtimeValidator()
            self.form_validation_service = EnhancedFormValidationService()

        except ImportError as e:
            pytest.skip(f"Required validation components not available: {e}")

    def test_single_field_validation_performance(self):
        """Test single field validation completes in <50ms."""
        # Test various field types and values
        test_cases = [
            ('account_size', '10000'),
            ('risk_percentage', '2.5'),
            ('entry_price', '50.00'),
            ('stop_loss_price', '48.00'),
            ('shares', '100'),
            ('contracts', '5'),
            ('premium', '2.50'),
            ('tick_value', '12.50'),
            ('ticks_at_risk', '8')
        ]

        for field_name, value in test_cases:
            start_time = time.perf_counter()

            # Perform validation
            result = self.validation_service.validate_field(field_name, value)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000  # Convert to ms

            assert validation_time < 50, f"Field '{field_name}' validation took {validation_time:.2f}ms, should be <50ms"

    def test_invalid_field_validation_performance(self):
        """Test validation performance with invalid inputs."""
        invalid_test_cases = [
            ('account_size', 'not_a_number'),
            ('risk_percentage', '150'),  # Too high
            ('entry_price', '-5'),       # Negative
            ('stop_loss_price', 'abc'),
            ('shares', '0'),             # Zero
            ('contracts', '-1'),         # Negative
            ('premium', ''),             # Empty
            ('tick_value', 'invalid'),
            ('ticks_at_risk', '0.5')     # Decimal where int expected
        ]

        for field_name, invalid_value in invalid_test_cases:
            start_time = time.perf_counter()

            # Perform validation (should fail but still be fast)
            result = self.validation_service.validate_field(field_name, invalid_value)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            assert validation_time < 50, f"Invalid field '{field_name}' validation took {validation_time:.2f}ms, should be <50ms"

    def test_complete_form_validation_performance(self):
        """Test complete form validation for all trade types in <50ms."""
        # Test data for each trade type
        form_data_sets = [
            # Equity percentage method
            {
                'trade_type': 'equity',
                'method': 'percentage',
                'account_size': '10000',
                'risk_percentage': '2',
                'entry_price': '50.00',
                'stop_loss_price': '48.00'
            },
            # Equity fixed amount method
            {
                'trade_type': 'equity',
                'method': 'fixed_amount',
                'account_size': '10000',
                'fixed_risk_amount': '200',
                'entry_price': '50.00',
                'stop_loss_price': '48.00'
            },
            # Options trade
            {
                'trade_type': 'option',
                'method': 'percentage',
                'account_size': '10000',
                'risk_percentage': '2',
                'premium': '2.50',
                'contracts': '1'
            },
            # Futures trade
            {
                'trade_type': 'future',
                'method': 'percentage',
                'account_size': '10000',
                'risk_percentage': '2',
                'tick_value': '12.50',
                'ticks_at_risk': '8'
            }
        ]

        for form_data in form_data_sets:
            start_time = time.perf_counter()

            # Validate complete form
            validation_result = self.form_validation_service.validate_form(form_data)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            trade_type = form_data['trade_type']
            method = form_data['method']
            assert validation_time < 50, f"Complete {trade_type} {method} form validation took {validation_time:.2f}ms, should be <50ms"

    def test_rapid_field_sequence_validation_performance(self):
        """Test validation performance during rapid field value changes."""
        field_sequences = [
            ('account_size', ['', '1', '10', '100', '1000', '10000', '25000', '50000']),
            ('risk_percentage', ['', '0', '0.5', '1', '1.5', '2', '2.5', '3']),
            ('entry_price', ['', '5', '10', '25', '50', '75', '100', '150']),
            ('stop_loss_price', ['', '3', '8', '20', '48', '70', '95', '145'])
        ]

        for field_name, value_sequence in field_sequences:
            start_time = time.perf_counter()

            # Validate each value in sequence rapidly
            for value in value_sequence:
                self.validation_service.validate_field(field_name, value)

            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            avg_time_per_validation = total_time / len(value_sequence)

            assert avg_time_per_validation < 50, f"Rapid {field_name} validation averaged {avg_time_per_validation:.2f}ms per validation, should be <50ms"

    def test_concurrent_field_validation_performance(self):
        """Test validation performance when multiple fields are validated simultaneously."""
        concurrent_fields = {
            'account_size': '10000',
            'risk_percentage': '2',
            'entry_price': '50.00',
            'stop_loss_price': '48.00',
            'shares': '100'
        }

        start_time = time.perf_counter()

        # Validate all fields
        validation_results = {}
        for field_name, value in concurrent_fields.items():
            validation_results[field_name] = self.validation_service.validate_field(field_name, value)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        assert total_time < 50, f"Concurrent validation of {len(concurrent_fields)} fields took {total_time:.2f}ms, should be <50ms"

    def test_realtime_validation_performance(self):
        """Test realtime validator performance with debouncing."""
        if not hasattr(self, 'realtime_validator'):
            pytest.skip("RealtimeValidator not available")

        field_name = 'account_size'
        rapid_values = ['1', '10', '100', '1000', '10000']

        start_time = time.perf_counter()

        # Simulate rapid typing with realtime validation
        for value in rapid_values:
            self.realtime_validator.validate_field_realtime(field_name, value)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000

        assert total_time < 50, f"Realtime validation sequence took {total_time:.2f}ms, should be <50ms"

    def test_validation_with_complex_rules_performance(self):
        """Test validation performance with complex business rules."""
        # Test complex validation scenarios
        complex_cases = [
            # Large numbers
            ('account_size', '999999999'),
            ('risk_percentage', '0.001'),  # Very small percentage
            ('entry_price', '999.9999'),   # High precision

            # Edge cases that require complex validation logic
            ('stop_loss_price', '49.9999'),  # Very close to entry price
            ('shares', '999999'),            # Large share count
            ('premium', '0.01'),             # Very small premium
        ]

        for field_name, complex_value in complex_cases:
            start_time = time.perf_counter()

            result = self.validation_service.validate_field(field_name, complex_value)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            assert validation_time < 50, f"Complex validation for '{field_name}' took {validation_time:.2f}ms, should be <50ms"

    def test_validation_error_message_generation_performance(self):
        """Test performance of error message generation."""
        # Invalid inputs that should generate detailed error messages
        error_cases = [
            ('account_size', '-1000'),     # Negative
            ('risk_percentage', '150'),    # Too high
            ('entry_price', '0'),          # Zero
            ('stop_loss_price', 'invalid'), # Non-numeric
            ('shares', '0.5'),             # Decimal where integer expected
        ]

        for field_name, invalid_value in error_cases:
            start_time = time.perf_counter()

            # Validate and generate error message
            result = self.validation_service.validate_field(field_name, invalid_value)
            if hasattr(result, 'error_message'):
                error_message = result.error_message

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            assert validation_time < 50, f"Validation with error message for '{field_name}' took {validation_time:.2f}ms, should be <50ms"

    def test_method_switching_validation_performance(self):
        """Test validation performance during risk method switching."""
        methods = ['percentage', 'fixed_amount', 'level']
        base_data = {
            'account_size': '10000',
            'entry_price': '50.00',
            'stop_loss_price': '48.00'
        }

        for method in methods:
            start_time = time.perf_counter()

            # Prepare data for specific method
            form_data = base_data.copy()
            if method == 'percentage':
                form_data['risk_percentage'] = '2'
            elif method == 'fixed_amount':
                form_data['fixed_risk_amount'] = '200'
            elif method == 'level':
                form_data['level'] = '1'

            # Validate form for method
            result = self.form_validation_service.validate_form_for_method(form_data, method)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            assert validation_time < 50, f"Method switching validation for '{method}' took {validation_time:.2f}ms, should be <50ms"

    def test_validation_cache_performance(self):
        """Test validation performance with caching enabled."""
        # Test repeated validation of same values (should benefit from caching)
        repeated_validations = [
            ('account_size', '10000'),
            ('risk_percentage', '2'),
            ('entry_price', '50.00'),
            ('stop_loss_price', '48.00')
        ]

        # First round - populate cache
        for field_name, value in repeated_validations:
            self.validation_service.validate_field(field_name, value)

        # Second round - should be faster due to caching
        start_time = time.perf_counter()

        for field_name, value in repeated_validations:
            result = self.validation_service.validate_field(field_name, value)

        end_time = time.perf_counter()
        cached_validation_time = (end_time - start_time) * 1000

        assert cached_validation_time < 25, f"Cached validation took {cached_validation_time:.2f}ms, should be <25ms (50% improvement)"

    def test_validation_performance_under_load(self):
        """Test validation performance under high load conditions."""
        # Simulate high load with many rapid validations
        load_test_fields = [
            'account_size', 'risk_percentage', 'entry_price', 'stop_loss_price',
            'shares', 'contracts', 'premium', 'tick_value', 'ticks_at_risk'
        ]

        load_test_values = [
            '10000', '2', '50.00', '48.00', '100', '5', '2.50', '12.50', '8'
        ]

        start_time = time.perf_counter()

        # Perform 100 validation operations rapidly
        for i in range(100):
            field_idx = i % len(load_test_fields)
            value_idx = i % len(load_test_values)

            field_name = load_test_fields[field_idx]
            value = load_test_values[value_idx]

            self.validation_service.validate_field(field_name, value)

        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        avg_validation_time = total_time / 100

        assert avg_validation_time < 50, f"High load validation averaged {avg_validation_time:.2f}ms per validation, should be <50ms"

    def test_validation_memory_efficiency(self):
        """Test that validation doesn't create memory leaks during performance testing."""
        import gc

        # Baseline memory measurement
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Perform many validations
        for i in range(1000):
            field_name = 'account_size'
            value = str(i * 10)
            self.validation_service.validate_field(field_name, value)

            # Periodically check that we're not accumulating objects
            if i % 100 == 0:
                gc.collect()
                current_objects = len(gc.get_objects())
                object_growth = current_objects - initial_objects

                # Allow some growth but not excessive
                assert object_growth < 1000, f"Excessive object growth during validation: {object_growth} new objects"

    def test_validation_performance_regression_detection(self):
        """Test to detect performance regressions in validation."""
        # Baseline performance test with known good values
        baseline_cases = [
            ('account_size', '10000'),
            ('risk_percentage', '2'),
            ('entry_price', '50.00'),
            ('stop_loss_price', '48.00')
        ]

        validation_times = []

        # Measure multiple iterations for statistical accuracy
        for iteration in range(10):
            for field_name, value in baseline_cases:
                start_time = time.perf_counter()
                result = self.validation_service.validate_field(field_name, value)
                end_time = time.perf_counter()

                validation_time = (end_time - start_time) * 1000
                validation_times.append(validation_time)

        # Calculate statistics
        avg_time = sum(validation_times) / len(validation_times)
        max_time = max(validation_times)

        # Performance requirements
        assert avg_time < 25, f"Average validation time {avg_time:.2f}ms exceeds 25ms baseline"
        assert max_time < 50, f"Maximum validation time {max_time:.2f}ms exceeds 50ms requirement"

        # Check for consistency (no outliers)
        outliers = [t for t in validation_times if t > avg_time * 3]
        assert len(outliers) == 0, f"Found {len(outliers)} performance outliers in validation timing"

    def test_validation_startup_time_performance(self):
        """Test validation service initialization performance."""
        start_time = time.perf_counter()

        # Initialize fresh validation service
        from risk_calculator.services.enhanced_validation_service import EnhancedValidationService
        fresh_service = EnhancedValidationService()

        # Perform first validation (may include lazy loading)
        fresh_service.validate_field('account_size', '10000')

        end_time = time.perf_counter()
        startup_time = (end_time - start_time) * 1000

        assert startup_time < 100, f"Validation service startup took {startup_time:.2f}ms, should be <100ms"

    @pytest.mark.parametrize("field_name,test_values", [
        ('account_size', ['1000', '10000', '100000', '1000000']),
        ('risk_percentage', ['0.5', '1', '2', '5', '10']),
        ('entry_price', ['1.00', '10.00', '100.00', '1000.00']),
        ('stop_loss_price', ['0.50', '9.00', '95.00', '950.00']),
    ])
    def test_parameterized_field_validation_performance(self, field_name, test_values):
        """Parameterized test for individual field validation performance."""
        for value in test_values:
            start_time = time.perf_counter()

            result = self.validation_service.validate_field(field_name, value)

            end_time = time.perf_counter()
            validation_time = (end_time - start_time) * 1000

            assert validation_time < 50, f"Field '{field_name}' with value '{value}' took {validation_time:.2f}ms, should be <50ms"