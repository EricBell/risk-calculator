"""Validation result model for encapsulating validation outcomes."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ValidationResult:
    """Encapsulates validation outcome for user feedback."""

    is_valid: bool
    error_messages: List[str] = field(default_factory=list)
    warning_messages: List[str] = field(default_factory=list)
    field_errors: Dict[str, str] = field(default_factory=dict)  # field_name -> error_message

    def add_error(self, field_name: str, message: str) -> None:
        """Add field-specific error."""
        self.field_errors[field_name] = message
        if message not in self.error_messages:
            self.error_messages.append(f"{field_name}: {message}")
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add warning message."""
        if message not in self.warning_messages:
            self.warning_messages.append(message)

    def clear_field_error(self, field_name: str) -> None:
        """Clear error for specific field."""
        if field_name in self.field_errors:
            old_message = self.field_errors[field_name]
            del self.field_errors[field_name]

            # Remove from error_messages list
            error_prefix = f"{field_name}: {old_message}"
            if error_prefix in self.error_messages:
                self.error_messages.remove(error_prefix)

        # Update is_valid status
        self.is_valid = len(self.field_errors) == 0

    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return not self.is_valid or len(self.field_errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warning_messages) > 0

    def get_all_messages(self) -> List[str]:
        """Get all error and warning messages."""
        return self.error_messages + self.warning_messages

    @property
    def warnings(self) -> List[str]:
        """Backward compatibility property for warning_messages."""
        return self.warning_messages