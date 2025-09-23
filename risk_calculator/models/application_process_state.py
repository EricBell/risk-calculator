"""
Application process state model for tracking application lifecycle and process management.
Part of Phase 3.3: Core Models implementation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import threading
import os


class ProcessState(Enum):
    """Application process state enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"
    ERROR = "error"
    SUSPENDED = "suspended"


class ProcessPhase(Enum):
    """Process lifecycle phases."""
    STARTUP = "startup"
    NORMAL_OPERATION = "normal_operation"
    CLEANUP = "cleanup"
    EXIT = "exit"


@dataclass
class ProcessEvent:
    """Model for tracking process events."""
    event_type: str
    timestamp: float
    phase: ProcessPhase
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_seconds(self) -> float:
        """Get age of this event in seconds."""
        return time.time() - self.timestamp


@dataclass
class ResourceInfo:
    """Information about system resources."""
    memory_usage_mb: float
    cpu_usage_percent: float
    thread_count: int
    file_handles: int
    timestamp: float

    @classmethod
    def current(cls) -> 'ResourceInfo':
        """
        Get current resource information.

        Returns:
            ResourceInfo with current system resource usage
        """
        try:
            import psutil
            process = psutil.Process()

            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            cpu_percent = process.cpu_percent()
            thread_count = process.num_threads()

            # Approximate file handles (not all platforms support this)
            try:
                file_handles = process.num_fds() if hasattr(process, 'num_fds') else 0
            except:
                file_handles = 0

            return cls(
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                thread_count=thread_count,
                file_handles=file_handles,
                timestamp=time.time()
            )
        except ImportError:
            # Fallback when psutil not available
            return cls(
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                thread_count=threading.active_count(),
                file_handles=0,
                timestamp=time.time()
            )


@dataclass
class ApplicationProcessState:
    """
    Model for tracking application process state and lifecycle.

    This model maintains the current state of the application process,
    tracks lifecycle events, manages cleanup handlers, and monitors
    system resources.
    """

    process_id: str
    current_state: ProcessState = ProcessState.INITIALIZING
    current_phase: ProcessPhase = ProcessPhase.STARTUP
    startup_time: Optional[float] = None
    shutdown_time: Optional[float] = None
    events: List[ProcessEvent] = field(default_factory=list)
    cleanup_handlers: List[Callable[[], None]] = field(default_factory=list)
    startup_handlers: List[Callable[[], None]] = field(default_factory=list)
    shutdown_handlers: List[Callable[[], None]] = field(default_factory=list)
    resource_history: List[ResourceInfo] = field(default_factory=list)
    error_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self):
        """Initialize process state after creation."""
        if self.startup_time is None:
            self.startup_time = time.time()

    def update_state(self, new_state: ProcessState, message: str = "",
                    metadata: Dict[str, Any] = None) -> None:
        """
        Update process state with event tracking.

        Args:
            new_state: New process state
            message: Optional message describing the state change
            metadata: Additional metadata for the event
        """
        with self._lock:
            if metadata is None:
                metadata = {}

            # Record event
            event = ProcessEvent(
                event_type=f"state_change_{new_state.value}",
                timestamp=time.time(),
                phase=self.current_phase,
                message=message or f"State changed to {new_state.value}",
                metadata=metadata.copy()
            )
            self.events.append(event)

            # Update state
            old_state = self.current_state
            self.current_state = new_state

            # Update special timestamps
            if new_state == ProcessState.RUNNING and old_state == ProcessState.INITIALIZING:
                self.startup_time = time.time()
            elif new_state == ProcessState.SHUTTING_DOWN:
                self.shutdown_time = time.time()

    def update_phase(self, new_phase: ProcessPhase, message: str = "") -> None:
        """
        Update process phase.

        Args:
            new_phase: New process phase
            message: Optional message describing the phase change
        """
        with self._lock:
            if new_phase != self.current_phase:
                event = ProcessEvent(
                    event_type=f"phase_change_{new_phase.value}",
                    timestamp=time.time(),
                    phase=self.current_phase,
                    message=message or f"Phase changed to {new_phase.value}"
                )
                self.events.append(event)
                self.current_phase = new_phase

    def add_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add a custom event to the process history.

        Args:
            event_type: Type of event
            message: Event message
            metadata: Additional event metadata
        """
        with self._lock:
            if metadata is None:
                metadata = {}

            event = ProcessEvent(
                event_type=event_type,
                timestamp=time.time(),
                phase=self.current_phase,
                message=message,
                metadata=metadata.copy()
            )
            self.events.append(event)

    def register_startup_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a startup handler.

        Args:
            handler: Function to call during startup
        """
        if handler not in self.startup_handlers:
            self.startup_handlers.append(handler)

    def register_shutdown_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a shutdown handler.

        Args:
            handler: Function to call during shutdown
        """
        if handler not in self.shutdown_handlers:
            self.shutdown_handlers.append(handler)

    def register_cleanup_handler(self, handler: Callable[[], None]) -> None:
        """
        Register a cleanup handler.

        Args:
            handler: Function to call during cleanup
        """
        if handler not in self.cleanup_handlers:
            self.cleanup_handlers.append(handler)

    def initialize_application(self) -> bool:
        """
        Initialize the application and call startup handlers.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.update_state(ProcessState.INITIALIZING, "Starting application initialization")
            self.update_phase(ProcessPhase.STARTUP)

            # Call startup handlers
            for handler in self.startup_handlers:
                try:
                    handler()
                except Exception as e:
                    self.add_event("startup_handler_error", f"Startup handler failed: {e}")

            self.update_state(ProcessState.RUNNING, "Application initialization complete")
            self.update_phase(ProcessPhase.NORMAL_OPERATION)
            return True

        except Exception as e:
            self.update_state(ProcessState.ERROR, f"Initialization failed: {e}")
            self.error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': time.time()
            }
            return False

    def shutdown_application(self) -> bool:
        """
        Shutdown the application gracefully and call shutdown handlers.

        Returns:
            True if shutdown successful, False otherwise
        """
        try:
            self.update_state(ProcessState.SHUTTING_DOWN, "Starting application shutdown")
            self.update_phase(ProcessPhase.CLEANUP)

            # Call shutdown handlers
            for handler in self.shutdown_handlers:
                try:
                    handler()
                except Exception as e:
                    self.add_event("shutdown_handler_error", f"Shutdown handler failed: {e}")

            # Call cleanup handlers
            self.force_cleanup()

            self.update_state(ProcessState.STOPPED, "Application shutdown complete")
            self.update_phase(ProcessPhase.EXIT)
            return True

        except Exception as e:
            self.update_state(ProcessState.ERROR, f"Shutdown failed: {e}")
            self.error_info = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': time.time()
            }
            return False

    def force_cleanup(self) -> None:
        """Force cleanup of all registered resources."""
        self.add_event("force_cleanup_start", "Starting force cleanup")

        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                self.add_event("cleanup_handler_error", f"Cleanup handler failed: {e}")

        self.add_event("force_cleanup_complete", "Force cleanup complete")

    def is_application_running(self) -> bool:
        """
        Check if application is currently running.

        Returns:
            True if running, False otherwise
        """
        return self.current_state == ProcessState.RUNNING

    def get_startup_time(self) -> Optional[float]:
        """
        Get application startup time in seconds.

        Returns:
            Startup time in seconds, or None if not started
        """
        if self.startup_time:
            return time.time() - self.startup_time
        return None

    def get_uptime(self) -> float:
        """
        Get application uptime in seconds.

        Returns:
            Uptime in seconds since startup
        """
        if self.startup_time:
            return time.time() - self.startup_time
        return 0.0

    def record_resource_usage(self) -> None:
        """Record current resource usage."""
        resource_info = ResourceInfo.current()
        self.resource_history.append(resource_info)

        # Keep only recent resource history (last 100 entries)
        if len(self.resource_history) > 100:
            self.resource_history = self.resource_history[-100:]

    def get_current_resource_usage(self) -> Optional[ResourceInfo]:
        """
        Get most recent resource usage information.

        Returns:
            Most recent ResourceInfo or None if no data
        """
        return self.resource_history[-1] if self.resource_history else None

    def get_average_resource_usage(self, minutes: int = 5) -> Optional[Dict[str, float]]:
        """
        Get average resource usage over specified time period.

        Args:
            minutes: Time period in minutes to average over

        Returns:
            Dictionary with average resource usage values
        """
        if not self.resource_history:
            return None

        cutoff_time = time.time() - (minutes * 60)
        recent_resources = [r for r in self.resource_history if r.timestamp >= cutoff_time]

        if not recent_resources:
            return None

        return {
            'memory_usage_mb': sum(r.memory_usage_mb for r in recent_resources) / len(recent_resources),
            'cpu_usage_percent': sum(r.cpu_usage_percent for r in recent_resources) / len(recent_resources),
            'thread_count': sum(r.thread_count for r in recent_resources) / len(recent_resources),
            'file_handles': sum(r.file_handles for r in recent_resources) / len(recent_resources)
        }

    def get_recent_events(self, count: int = 10) -> List[ProcessEvent]:
        """
        Get recent process events.

        Args:
            count: Number of recent events to return

        Returns:
            List of recent events
        """
        return self.events[-count:] if self.events else []

    def get_process_summary(self) -> Dict[str, Any]:
        """
        Get summary of current process state.

        Returns:
            Dictionary with process summary information
        """
        current_resources = self.get_current_resource_usage()
        avg_resources = self.get_average_resource_usage()

        return {
            'process_id': self.process_id,
            'current_state': self.current_state.value,
            'current_phase': self.current_phase.value,
            'is_running': self.is_application_running(),
            'uptime_seconds': self.get_uptime(),
            'startup_time': self.startup_time,
            'shutdown_time': self.shutdown_time,
            'event_count': len(self.events),
            'cleanup_handlers': len(self.cleanup_handlers),
            'startup_handlers': len(self.startup_handlers),
            'shutdown_handlers': len(self.shutdown_handlers),
            'current_resources': current_resources.__dict__ if current_resources else None,
            'average_resources': avg_resources,
            'error_info': self.error_info,
            'metadata': self.metadata
        }

    def clear_old_events(self, max_age_hours: int = 24) -> None:
        """
        Clear old events to prevent memory accumulation.

        Args:
            max_age_hours: Maximum age of events to keep in hours
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        self.events = [e for e in self.events if e.timestamp >= cutoff_time]

    def copy(self) -> 'ApplicationProcessState':
        """
        Create a copy of the process state.

        Returns:
            New ApplicationProcessState instance with copied data
        """
        new_state = ApplicationProcessState(
            process_id=self.process_id,
            current_state=self.current_state,
            current_phase=self.current_phase,
            startup_time=self.startup_time,
            shutdown_time=self.shutdown_time,
            error_info=self.error_info.copy() if self.error_info else None,
            metadata=self.metadata.copy()
        )

        # Copy events
        new_state.events = [
            ProcessEvent(
                event_type=e.event_type,
                timestamp=e.timestamp,
                phase=e.phase,
                message=e.message,
                metadata=e.metadata.copy()
            )
            for e in self.events
        ]

        # Copy resource history
        new_state.resource_history = [
            ResourceInfo(
                memory_usage_mb=r.memory_usage_mb,
                cpu_usage_percent=r.cpu_usage_percent,
                thread_count=r.thread_count,
                file_handles=r.file_handles,
                timestamp=r.timestamp
            )
            for r in self.resource_history
        ]

        return new_state

    @classmethod
    def create_new(cls, process_id: str) -> 'ApplicationProcessState':
        """
        Create a new application process state.

        Args:
            process_id: Unique identifier for the process

        Returns:
            New ApplicationProcessState instance
        """
        return cls(process_id=process_id)

    def __repr__(self) -> str:
        """String representation of process state."""
        return (f"ApplicationProcessState(id='{self.process_id}', "
                f"state={self.current_state.value}, "
                f"phase={self.current_phase.value}, "
                f"uptime={self.get_uptime():.1f}s)")