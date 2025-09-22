"""
Qt Configuration Persistence Service
Handles saving and loading application configuration using QSettings.
"""

from typing import Any, Dict, Optional, Union
from datetime import datetime
from pathlib import Path
import json

try:
    from PySide6.QtCore import QSettings
    HAS_QT = True
except ImportError:
    HAS_QT = False

from ..models.window_configuration import WindowConfiguration
from ..models.display_profile import DisplayProfile
from ..models.ui_layout_state import UILayoutState


class QtConfigurationService:
    """Qt-based configuration persistence service using QSettings."""

    def __init__(self, organization_name: str = "RiskCalculator",
                 application_name: str = "MainApp"):
        """
        Initialize Qt configuration service.

        Args:
            organization_name: Organization name for settings
            application_name: Application name for settings
        """
        if not HAS_QT:
            raise ImportError("PySide6 not available - Qt configuration service not supported")

        self.settings = QSettings(organization_name, application_name)

    def save_window_configuration(self, config: WindowConfiguration) -> bool:
        """
        Save window configuration.

        Args:
            config: Window configuration to save

        Returns:
            bool: True if saved successfully
        """
        try:
            config_dict = config.to_dict()

            self.settings.beginGroup("window")
            for key, value in config_dict.items():
                if isinstance(value, datetime):
                    value = value.isoformat()
                self.settings.setValue(key, value)
            self.settings.endGroup()

            self.settings.sync()
            return True

        except Exception:
            return False

    def load_window_configuration(self) -> Optional[WindowConfiguration]:
        """
        Load window configuration.

        Returns:
            WindowConfiguration or None if not found
        """
        try:
            self.settings.beginGroup("window")
            keys = self.settings.allKeys()

            if not keys:
                self.settings.endGroup()
                return None

            config_dict = {}
            for key in keys:
                value = self.settings.value(key)
                if key == "last_updated" and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                config_dict[key] = value

            self.settings.endGroup()

            return WindowConfiguration.from_dict(config_dict)

        except Exception:
            return None

    def save_display_profile(self, profile: DisplayProfile) -> bool:
        """
        Save display profile for current session.

        Args:
            profile: Display profile to save

        Returns:
            bool: True if saved successfully
        """
        try:
            profile_dict = profile.to_dict()

            self.settings.beginGroup("display")
            for key, value in profile_dict.items():
                self.settings.setValue(key, value)
            self.settings.endGroup()

            self.settings.sync()
            return True

        except Exception:
            return False

    def load_display_profile(self) -> Optional[DisplayProfile]:
        """
        Load saved display profile.

        Returns:
            DisplayProfile or None if not found
        """
        try:
            self.settings.beginGroup("display")
            keys = self.settings.allKeys()

            if not keys:
                self.settings.endGroup()
                return None

            profile_dict = {}
            for key in keys:
                profile_dict[key] = self.settings.value(key)

            self.settings.endGroup()

            return DisplayProfile.from_dict(profile_dict)

        except Exception:
            return None

    def save_ui_layout_state(self, state: UILayoutState) -> bool:
        """
        Save UI layout state.

        Args:
            state: UI layout state to save

        Returns:
            bool: True if saved successfully
        """
        try:
            state_dict = state.to_dict()

            self.settings.beginGroup("layout")
            for key, value in state_dict.items():
                self.settings.setValue(key, value)
            self.settings.endGroup()

            self.settings.sync()
            return True

        except Exception:
            return False

    def load_ui_layout_state(self) -> Optional[UILayoutState]:
        """
        Load UI layout state.

        Returns:
            UILayoutState or None if not found
        """
        try:
            self.settings.beginGroup("layout")
            keys = self.settings.allKeys()

            if not keys:
                self.settings.endGroup()
                return None

            state_dict = {}
            for key in keys:
                state_dict[key] = self.settings.value(key)

            self.settings.endGroup()

            return UILayoutState.from_dict(state_dict)

        except Exception:
            return None

    def save_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Save user preferences.

        Args:
            preferences: Dictionary of user preferences

        Returns:
            bool: True if saved successfully
        """
        try:
            self.settings.beginGroup("preferences")

            for key, value in preferences.items():
                # Handle complex types by converting to JSON
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                self.settings.setValue(key, value)

            self.settings.endGroup()
            self.settings.sync()
            return True

        except Exception:
            return False

    def load_user_preferences(self) -> Dict[str, Any]:
        """
        Load user preferences.

        Returns:
            Dict[str, Any]: User preferences dictionary
        """
        try:
            self.settings.beginGroup("preferences")
            keys = self.settings.allKeys()

            preferences = {}
            for key in keys:
                value = self.settings.value(key)

                # Try to parse JSON for complex types
                if isinstance(value, str):
                    try:
                        parsed_value = json.loads(value)
                        if isinstance(parsed_value, (dict, list)):
                            value = parsed_value
                    except (json.JSONDecodeError, ValueError):
                        # Keep as string if not valid JSON
                        pass

                preferences[key] = value

            self.settings.endGroup()
            return preferences

        except Exception:
            return {}

    def save_form_data(self, form_name: str, form_data: Dict[str, str]) -> bool:
        """
        Save form data for persistence across sessions.

        Args:
            form_name: Name of the form (e.g., "equity", "options", "futures")
            form_data: Form field data

        Returns:
            bool: True if saved successfully
        """
        try:
            self.settings.beginGroup(f"forms/{form_name}")

            for field_name, field_value in form_data.items():
                self.settings.setValue(field_name, field_value)

            self.settings.endGroup()
            self.settings.sync()
            return True

        except Exception:
            return False

    def load_form_data(self, form_name: str) -> Dict[str, str]:
        """
        Load saved form data.

        Args:
            form_name: Name of the form

        Returns:
            Dict[str, str]: Form field data
        """
        try:
            self.settings.beginGroup(f"forms/{form_name}")
            keys = self.settings.allKeys()

            form_data = {}
            for key in keys:
                value = self.settings.value(key)
                # Ensure string values for form fields
                form_data[key] = str(value) if value is not None else ""

            self.settings.endGroup()
            return form_data

        except Exception:
            return {}

    def clear_form_data(self, form_name: str) -> bool:
        """
        Clear saved form data for a specific form.

        Args:
            form_name: Name of the form to clear

        Returns:
            bool: True if cleared successfully
        """
        try:
            self.settings.beginGroup(f"forms/{form_name}")
            self.settings.remove("")  # Remove all keys in group
            self.settings.endGroup()
            self.settings.sync()
            return True

        except Exception:
            return False

    def get_configuration_path(self) -> str:
        """
        Get the file path where configuration is stored.

        Returns:
            str: Configuration file path
        """
        return self.settings.fileName()

    def export_configuration(self, file_path: Union[str, Path]) -> bool:
        """
        Export all configuration to a file.

        Args:
            file_path: Path to export file

        Returns:
            bool: True if exported successfully
        """
        try:
            export_data = {
                "window": {},
                "display": {},
                "layout": {},
                "preferences": {},
                "forms": {}
            }

            # Export window configuration
            self.settings.beginGroup("window")
            for key in self.settings.allKeys():
                export_data["window"][key] = self.settings.value(key)
            self.settings.endGroup()

            # Export display profile
            self.settings.beginGroup("display")
            for key in self.settings.allKeys():
                export_data["display"][key] = self.settings.value(key)
            self.settings.endGroup()

            # Export layout state
            self.settings.beginGroup("layout")
            for key in self.settings.allKeys():
                export_data["layout"][key] = self.settings.value(key)
            self.settings.endGroup()

            # Export preferences
            self.settings.beginGroup("preferences")
            for key in self.settings.allKeys():
                export_data["preferences"][key] = self.settings.value(key)
            self.settings.endGroup()

            # Export form data
            self.settings.beginGroup("forms")
            for form_group in self.settings.childGroups():
                self.settings.beginGroup(form_group)
                export_data["forms"][form_group] = {}
                for key in self.settings.allKeys():
                    export_data["forms"][form_group][key] = self.settings.value(key)
                self.settings.endGroup()
            self.settings.endGroup()

            # Write to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            return True

        except Exception:
            return False

    def clear_all_configuration(self) -> bool:
        """
        Clear all saved configuration.

        Returns:
            bool: True if cleared successfully
        """
        try:
            self.settings.clear()
            self.settings.sync()
            return True

        except Exception:
            return False

    def get_settings_info(self) -> Dict[str, Any]:
        """
        Get information about current settings.

        Returns:
            Dict[str, Any]: Settings information
        """
        try:
            return {
                "file_path": self.settings.fileName(),
                "format": self.settings.format().name if hasattr(self.settings.format(), 'name') else "Unknown",
                "organization": self.settings.organizationName(),
                "application": self.settings.applicationName(),
                "all_keys": self.settings.allKeys(),
                "child_groups": self.settings.childGroups(),
                "is_writable": self.settings.isWritable()
            }

        except Exception as e:
            return {"error": str(e)}