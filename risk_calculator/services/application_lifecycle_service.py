"""
Application lifecycle management service implementation.
Part of Phase 3.4: Validation Services implementation.
"""

from typing import List, Optional, Callable, Dict, Any
import time
import threading
import atexit
import signal
import sys

from ..models.application_process_state import ApplicationProcessState, ProcessState, ProcessPhase


class ApplicationLifecycleService:
    """
    Application lifecycle management service implementing ApplicationLifecycleInterface.

    This service manages the complete application lifecycle including startup,
    shutdown, cleanup, and resource management.
    """

    def __init__(self, process_id: str = "risk_calculator_main"):
        """
        Initialize the application lifecycle service.

        Args:
            process_id: Unique identifier for this process
        """
        self.process_state = ApplicationProcessState.create_new(process_id)
        self._initialized = False
        self._shutdown_in_progress = False
        self._startup_duration = None

        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()

        # Register atexit handler
        atexit.register(self._atexit_handler)

    def register_startup_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a handler to be called during application startup.

        Args:
            handler: Function to call during startup
        """
        self.process_state.register_startup_handler(handler)

    def register_shutdown_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a handler to be called during application shutdown.

        Args:
            handler: Function to call during shutdown
        """
        self.process_state.register_shutdown_handler(handler)

    def register_cleanup_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a cleanup handler for resources.

        Args:
            handler: Function to call during cleanup
        """
        self.process_state.register_cleanup_handler(handler)

    def initialize_application(self) -> bool:
        """
        Initialize the application and call startup handlers.

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            self.process_state.add_event("init_already_initialized", "Application already initialized")
            return True

        try:
            start_time = time.time()
            self.process_state.add_event("init_start", "Application initialization starting")

            # Initialize application state
            success = self.process_state.initialize_application()

            if success:
                self._startup_duration = time.time() - start_time
                self._initialized = True
                self.process_state.add_event(
                    "init_complete",
                    f"Application initialization completed in {self._startup_duration:.3f}s"
                )

                # Start resource monitoring
                self._start_resource_monitoring()

                return True
            else:
                self.process_state.add_event("init_failed", "Application initialization failed")
                return False

        except Exception as e:
            self.process_state.add_event("init_error", f"Application initialization error: {e}")
            return False

    def shutdown_application(self) -> bool:
        """
        Shutdown the application gracefully and call shutdown handlers.

        Returns:
            True if shutdown successful, False otherwise
        """
        if self._shutdown_in_progress:
            self.process_state.add_event("shutdown_already_in_progress", "Shutdown already in progress")
            return True

        if not self._initialized:
            self.process_state.add_event("shutdown_not_initialized", "Application was not initialized")
            return True

        try:
            self._shutdown_in_progress = True
            start_time = time.time()

            self.process_state.add_event("shutdown_start", "Application shutdown starting")

            # Stop resource monitoring
            self._stop_resource_monitoring()

            # Perform shutdown
            success = self.process_state.shutdown_application()

            shutdown_duration = time.time() - start_time

            if success:
                self.process_state.add_event(
                    "shutdown_complete",
                    f"Application shutdown completed in {shutdown_duration:.3f}s"
                )
                self._initialized = False
                return True
            else:
                self.process_state.add_event("shutdown_failed", "Application shutdown failed")
                return False

        except Exception as e:
            self.process_state.add_event("shutdown_error", f"Application shutdown error: {e}")
            return False
        finally:
            self._shutdown_in_progress = False

    def is_application_running(self) -> bool:
        """
        Check if application is currently running.

        Returns:
            True if running, False otherwise
        """
        return self.process_state.is_application_running()

    def get_startup_time(self) -> Optional[float]:
        """
        Get application startup time in seconds.

        Returns:
            Startup time in seconds, or None if not started
        """
        return self._startup_duration

    def force_cleanup(self) -> None:
        """Force cleanup of all registered resources."""
        self.process_state.add_event("force_cleanup_requested", "Force cleanup requested")
        self.process_state.force_cleanup()

    def get_process_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive process summary.

        Returns:
            Dictionary with detailed process information
        """
        summary = self.process_state.get_process_summary()
        summary.update({
            'initialized': self._initialized,
            'shutdown_in_progress': self._shutdown_in_progress,
            'startup_duration': self._startup_duration
        })
        return summary

    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent process events.

        Args:
            count: Number of recent events to return

        Returns:
            List of recent events
        """
        events = self.process_state.get_recent_events(count)
        return [
            {
                'event_type': event.event_type,
                'timestamp': event.timestamp,
                'phase': event.phase.value,
                'message': event.message,
                'age_seconds': event.age_seconds,
                'metadata': event.metadata
            }
            for event in events
        ]

    def get_uptime(self) -> float:
        """
        Get application uptime in seconds.

        Returns:
            Uptime in seconds since startup
        """
        return self.process_state.get_uptime()

    def get_resource_usage(self) -> Optional[Dict[str, Any]]:
        """
        Get current resource usage.

        Returns:
            Dictionary with current resource usage or None
        """
        current_resources = self.process_state.get_current_resource_usage()
        if current_resources:
            return {
                'memory_usage_mb': current_resources.memory_usage_mb,
                'cpu_usage_percent': current_resources.cpu_usage_percent,
                'thread_count': current_resources.thread_count,
                'file_handles': current_resources.file_handles,
                'timestamp': current_resources.timestamp
            }
        return None

    def get_average_resource_usage(self, minutes: int = 5) -> Optional[Dict[str, float]]:
        """
        Get average resource usage over specified time period.

        Args:
            minutes: Time period in minutes to average over

        Returns:
            Dictionary with average resource usage values
        """
        return self.process_state.get_average_resource_usage(minutes)

    def add_custom_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a custom event to the process history.

        Args:
            event_type: Type of event
            message: Event message
            metadata: Additional event metadata
        """
        self.process_state.add_event(event_type, message, metadata or {})

    def check_performance_thresholds(self) -> Dict[str, bool]:
        """
        Check if application meets performance thresholds.

        Returns:
            Dictionary indicating which thresholds are met
        """
        thresholds = {
            'startup_time_under_3s': True,
            'memory_under_100mb': True,
            'response_time_under_100ms': True,
            'exit_time_under_2s': True
        }

        # Check startup time
        if self._startup_duration is not None:
            thresholds['startup_time_under_3s'] = self._startup_duration < 3.0

        # Check memory usage
        current_resources = self.process_state.get_current_resource_usage()
        if current_resources:
            thresholds['memory_under_100mb'] = current_resources.memory_usage_mb < 100.0

        return thresholds

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.process_state.add_event(
                "signal_received",
                f"Received signal {signum}, initiating graceful shutdown"
            )
            self.shutdown_application()
            sys.exit(0)

        # Register handlers for common termination signals
        try:
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        except (AttributeError, ValueError):
            # Some signals may not be available on all platforms
            pass

    def _atexit_handler(self) -> None:
        """Handler called at program exit."""
        if self._initialized and not self._shutdown_in_progress:
            self.process_state.add_event("atexit_cleanup", "Performing cleanup at exit")
            self.force_cleanup()

    def _start_resource_monitoring(self) -> None:
        """Start background resource monitoring."""
        def monitor_resources():
            while self._initialized and not self._shutdown_in_progress:
                try:
                    self.process_state.record_resource_usage()
                    time.sleep(30)  # Record every 30 seconds
                except Exception as e:
                    self.process_state.add_event(
                        "resource_monitor_error",
                        f"Resource monitoring error: {e}"
                    )
                    break

        if self._initialized:
            monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
            monitor_thread.start()
            self.process_state.add_event("resource_monitor_start", "Resource monitoring started")

    def _stop_resource_monitoring(self) -> None:
        """Stop background resource monitoring."""
        # Resource monitoring will stop automatically when _initialized becomes False
        self.process_state.add_event("resource_monitor_stop", "Resource monitoring stopped")

    def emergency_shutdown(self) -> None:
        """Perform emergency shutdown without normal cleanup."""
        self.process_state.add_event("emergency_shutdown", "Emergency shutdown initiated")
        self.process_state.update_state(ProcessState.ERROR, "Emergency shutdown")

        # Attempt minimal cleanup
        try:
            self.force_cleanup()
        except Exception as e:
            self.process_state.add_event("emergency_cleanup_error", f"Emergency cleanup failed: {e}")

        self._initialized = False
        self._shutdown_in_progress = True

    def restart_application(self) -> bool:
        """
        Restart the application (shutdown then initialize).

        Returns:
            True if restart successful, False otherwise
        """
        self.process_state.add_event("restart_requested", "Application restart requested")

        # Shutdown first
        shutdown_success = self.shutdown_application()
        if not shutdown_success:
            self.process_state.add_event("restart_shutdown_failed", "Restart failed: shutdown unsuccessful")
            return False

        # Brief pause before restart
        time.sleep(0.1)

        # Initialize again
        init_success = self.initialize_application()
        if init_success:
            self.process_state.add_event("restart_complete", "Application restart completed successfully")
        else:
            self.process_state.add_event("restart_init_failed", "Restart failed: initialization unsuccessful")

        return init_success

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the application.

        Returns:
            Dictionary with health status information
        """
        current_resources = self.process_state.get_current_resource_usage()
        performance_thresholds = self.check_performance_thresholds()

        health_score = sum(performance_thresholds.values()) / len(performance_thresholds)

        return {
            'overall_health': 'healthy' if health_score >= 0.75 else 'degraded' if health_score >= 0.5 else 'unhealthy',
            'health_score': health_score,
            'is_running': self.is_application_running(),
            'uptime_seconds': self.get_uptime(),
            'performance_thresholds': performance_thresholds,
            'current_state': self.process_state.current_state.value,
            'current_phase': self.process_state.current_phase.value,
            'memory_usage_mb': current_resources.memory_usage_mb if current_resources else None,
            'error_info': self.process_state.error_info,
            'last_updated': time.time()
        }