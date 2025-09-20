"""Main application window with ttk.Notebook tab container and menu system."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Dict, Optional, Any, Callable
import sys
import os
from .equity_tab import EquityTab
from .option_tab import OptionsTab
from .future_tab import FuturesTab


class MainWindow:
    """Main application window with tabbed interface for different asset types."""

    def __init__(self, controller=None):
        self.controller = controller
        self.root = tk.Tk()
        self.tabs: Dict[str, Any] = {}
        self.current_tab_name: Optional[str] = None

        # Configure root window
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._setup_keyboard_shortcuts()
        self._center_window()

        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind("<KeyPress>", self._on_keypress)

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Risk Calculator - Daytrading Position Sizing")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)

        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Set application icon (if available)
        try:
            # Try to load icon from resources
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # Ignore if icon not found

        # Configure style for better cross-platform appearance
        self.style = ttk.Style()
        self._configure_styles()

    def _configure_styles(self) -> None:
        """Configure TTK styles for consistent appearance."""
        try:
            # Use a modern theme if available
            available_themes = self.style.theme_names()
            if 'clam' in available_themes:
                self.style.theme_use('clam')
            elif 'alt' in available_themes:
                self.style.theme_use('alt')

            # Configure custom styles
            self.style.configure('Title.TLabel', font=('TkDefaultFont', 12, 'bold'))
            self.style.configure('Error.TLabel', foreground='red')
            self.style.configure('Warning.TLabel', foreground='orange')
            self.style.configure('Success.TLabel', foreground='green')

        except Exception:
            pass  # Use default styles if configuration fails

    def _create_menu(self) -> None:
        """Create the application menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Calculation", command=self._new_calculation, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Current Tab", command=self._clear_current_tab, accelerator="Ctrl+R")
        edit_menu.add_command(label="Clear All Tabs", command=self._clear_all_tabs, accelerator="Ctrl+Shift+R")

        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Equity Tab", command=lambda: self.select_tab('equity'), accelerator="Ctrl+1")
        view_menu.add_command(label="Options Tab", command=lambda: self.select_tab('option'), accelerator="Ctrl+2")
        view_menu.add_command(label="Futures Tab", command=lambda: self.select_tab('future'), accelerator="Ctrl+3")

        # Tools menu
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Calculate Position", command=self._calculate_current, accelerator="Ctrl+Enter")

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="About Risk Methods", command=self._show_risk_methods_help)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_interface(self) -> None:
        """Create the main interface with tabbed notebook."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="5")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Status bar at top
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.status_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ttk.Label(self.status_frame, text="Ready", relief="sunken")
        self.status_label.grid(row=0, column=0, sticky="ew")

        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=(10, 0))
        self.progress_bar.grid_remove()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")

        # Bind tab selection event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Create tabs
        self._create_tabs()

    def _create_tabs(self) -> None:
        """Create individual trading tabs."""
        # Create Equity tab
        if self.controller:
            equity_controller = self.controller.create_equity_controller(None)
            self.tabs['equity'] = EquityTab(self.notebook, equity_controller)
            equity_controller.view = self.tabs['equity']  # Set view reference
        else:
            self.tabs['equity'] = EquityTab(self.notebook)

        self.notebook.add(self.tabs['equity'], text="Equity Trading")

        # Create Options tab
        if self.controller:
            option_controller = self.controller.create_option_controller(None)
            self.tabs['option'] = OptionsTab(self.notebook, option_controller)
            option_controller.view = self.tabs['option']  # Set view reference
        else:
            self.tabs['option'] = OptionsTab(self.notebook)

        self.notebook.add(self.tabs['option'], text="Options Trading")

        # Create Futures tab
        if self.controller:
            future_controller = self.controller.create_future_controller(None)
            self.tabs['future'] = FuturesTab(self.notebook, future_controller)
            future_controller.view = self.tabs['future']  # Set view reference
        else:
            self.tabs['future'] = FuturesTab(self.notebook)

        self.notebook.add(self.tabs['future'], text="Futures Trading")

        # Set initial tab
        self.current_tab_name = 'equity'
        self.notebook.select(0)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Global shortcuts
        self.root.bind_all("<Control-n>", lambda e: self._new_calculation())
        self.root.bind_all("<Control-q>", lambda e: self._on_closing())
        self.root.bind_all("<Control-r>", lambda e: self._clear_current_tab())
        self.root.bind_all("<Control-Shift-R>", lambda e: self._clear_all_tabs())
        self.root.bind_all("<Control-Return>", lambda e: self._calculate_current())
        self.root.bind_all("<Control-1>", lambda e: self.select_tab('equity'))
        self.root.bind_all("<Control-2>", lambda e: self.select_tab('option'))
        self.root.bind_all("<Control-3>", lambda e: self.select_tab('future'))
        self.root.bind_all("<F1>", lambda e: self._show_shortcuts())
        self.root.bind_all("<Escape>", lambda e: self.root.focus_set())

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _on_tab_changed(self, event) -> None:
        """Handle tab change events."""
        try:
            selected_tab = event.widget.select()
            tab_index = event.widget.index(selected_tab)

            # Map tab index to tab name
            tab_names = ['equity', 'option', 'future']
            if 0 <= tab_index < len(tab_names):
                self.current_tab_name = tab_names[tab_index]

                # Notify controller of tab change
                if self.controller:
                    self.controller.on_tab_changed(self.current_tab_name)

                # Update status
                tab_titles = {
                    'equity': 'Equity Trading - Stock Position Sizing',
                    'option': 'Options Trading - Contract Position Sizing',
                    'future': 'Futures Trading - Contract Position Sizing'
                }
                self.set_status(tab_titles.get(self.current_tab_name, 'Ready'))

                # Focus first input of new tab
                if self.current_tab_name in self.tabs:
                    tab = self.tabs[self.current_tab_name]
                    if hasattr(tab, 'focus_first_input'):
                        self.root.after(100, tab.focus_first_input)  # Small delay for smooth transition

        except Exception as e:
            # Handle tab change errors gracefully
            self.show_error(f"Tab change error: {str(e)}")

    def _on_keypress(self, event) -> None:
        """Handle global keypress events."""
        if self.controller and hasattr(self.controller, 'handle_global_keyboard_shortcut'):
            if self.controller.handle_global_keyboard_shortcut(event):
                return "break"

    # Public interface methods
    def select_tab(self, tab_name: str) -> None:
        """Programmatically select a tab."""
        tab_indices = {'equity': 0, 'option': 1, 'future': 2}
        if tab_name in tab_indices:
            self.notebook.select(tab_indices[tab_name])

    def set_title(self, title: str) -> None:
        """Set the window title."""
        self.root.title(title)

    def set_status(self, message: str) -> None:
        """Set the status message."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()

    def show_progress(self, show: bool = True) -> None:
        """Show or hide progress indication."""
        if show:
            self.progress_bar.grid()
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()

    def show_error(self, message: str) -> None:
        """Show error message."""
        messagebox.showerror("Error", message, parent=self.root)
        self.set_status(f"Error: {message}")

    def show_warning(self, message: str) -> None:
        """Show warning message."""
        messagebox.showwarning("Warning", message, parent=self.root)
        self.set_status(f"Warning: {message}")

    def show_info(self, message: str) -> None:
        """Show information message."""
        messagebox.showinfo("Information", message, parent=self.root)

    def confirm_action(self, message: str, title: str = "Confirm") -> bool:
        """Show confirmation dialog."""
        return messagebox.askyesno(title, message, parent=self.root)

    def update_tab_specific_ui(self, tab_name: str) -> None:
        """Update UI elements specific to the selected tab."""
        # This method can be extended for tab-specific UI updates
        pass

    # Menu command methods
    def _new_calculation(self) -> None:
        """Start a new calculation (clear current tab)."""
        self._clear_current_tab()

    def _clear_current_tab(self) -> None:
        """Clear the current tab."""
        if self.controller:
            self.controller.clear_current_tab()
        self.set_status("Current tab cleared")

    def _clear_all_tabs(self) -> None:
        """Clear all tabs."""
        if self.confirm_action("Clear all tabs? This will remove all entered data."):
            if self.controller:
                self.controller.clear_all_tabs()
            self.set_status("All tabs cleared")

    def _calculate_current(self) -> None:
        """Calculate position for current tab."""
        if self.controller:
            if not self.controller.is_any_calculation_in_progress():
                self.controller.calculate_current_tab()
            else:
                self.show_warning("Calculation already in progress")
        self.set_status("Calculating position...")

    def _show_shortcuts(self) -> None:
        """Show keyboard shortcuts help."""
        shortcuts_text = """Keyboard Shortcuts:

Navigation:
Ctrl+1, Ctrl+2, Ctrl+3 - Switch between tabs
Tab - Move to next field
Shift+Tab - Move to previous field

Actions:
Ctrl+Enter - Calculate position
Ctrl+N - New calculation (clear current tab)
Ctrl+R - Clear current tab
Ctrl+Shift+R - Clear all tabs

Application:
F1 - Show this help
Escape - Clear focus
Ctrl+Q - Exit application

Tab-specific:
Enter - Calculate position (when in input field)
Arrow keys - Navigate between radio buttons"""

        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text, parent=self.root)

    def _show_risk_methods_help(self) -> None:
        """Show help about risk calculation methods."""
        help_text = """Risk Calculation Methods:

1. Percentage Method:
   • Risk a fixed percentage of account (1-5%)
   • Requires: Entry price, Stop loss price
   • Formula: Position = (Account × Risk%) ÷ (Entry - Stop)

2. Fixed Amount Method:
   • Risk a fixed dollar amount ($10-500)
   • Requires: Entry price, Stop loss price
   • Formula: Position = Fixed Amount ÷ (Entry - Stop)

3. Level-Based Method:
   • Risk based on support/resistance levels
   • Automatically uses 2% of account as risk
   • Requires: Entry price, Support/resistance level
   • Not available for options trading

Asset-Specific Notes:
• Equities: All methods supported
• Options: Only percentage and fixed amount
• Futures: All methods with margin considerations"""

        messagebox.showinfo("Risk Calculation Methods", help_text, parent=self.root)

    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """Risk Calculator v1.0

A cross-platform desktop application for daytrading
position sizing calculations.

Features:
• Three risk calculation methods
• Support for stocks, options, and futures
• Real-time input validation
• Cross-platform compatibility (Windows/Linux)

Technology:
• Python 3.12+ with Tkinter
• MVC architecture pattern
• Decimal precision for financial calculations

Copyright © 2024
Built with Python and Tkinter"""

        messagebox.showinfo("About Risk Calculator", about_text, parent=self.root)

    def _on_closing(self) -> None:
        """Handle application closing."""
        if self.controller and hasattr(self.controller, 'shutdown'):
            try:
                self.controller.shutdown()
            except Exception:
                pass  # Ignore shutdown errors

        self.root.quit()
        self.root.destroy()

    # Application lifecycle methods
    def run(self) -> None:
        """Start the application main loop."""
        try:
            # Set initial focus
            if 'equity' in self.tabs and hasattr(self.tabs['equity'], 'focus_first_input'):
                self.root.after(100, self.tabs['equity'].focus_first_input)

            self.set_status("Application ready - Select a tab to begin")
            self.root.mainloop()

        except KeyboardInterrupt:
            self._on_closing()
        except Exception as e:
            self.show_error(f"Application error: {str(e)}")
            self._on_closing()

    def get_current_tab(self) -> Optional[Any]:
        """Get the currently selected tab widget."""
        if self.current_tab_name and self.current_tab_name in self.tabs:
            return self.tabs[self.current_tab_name]
        return None

    def set_tab_enabled(self, tab_name: str, enabled: bool) -> None:
        """Enable or disable a specific tab."""
        if tab_name in self.tabs:
            tab_indices = {'equity': 0, 'option': 1, 'future': 2}
            if tab_name in tab_indices:
                state = "normal" if enabled else "disabled"
                self.notebook.tab(tab_indices[tab_name], state=state)

    def add_custom_tab(self, tab_name: str, tab_widget: Any, display_name: str) -> None:
        """Add a custom tab (for future extensibility)."""
        self.tabs[tab_name] = tab_widget
        self.notebook.add(tab_widget, text=display_name)

    def get_window_geometry(self) -> str:
        """Get current window geometry for session persistence."""
        return self.root.geometry()

    def set_window_geometry(self, geometry: str) -> None:
        """Set window geometry from saved session."""
        try:
            self.root.geometry(geometry)
        except Exception:
            pass  # Use default geometry if invalid

    def minimize_to_tray(self) -> None:
        """Minimize window (placeholder for future system tray support)."""
        self.root.iconify()

    def restore_from_tray(self) -> None:
        """Restore window from minimized state."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def set_controller(self, controller) -> None:
        """Set the controller and recreate tabs with proper controller references."""
        self.controller = controller

        # Clear existing tabs
        for tab_name in list(self.tabs.keys()):
            self.notebook.forget(self.tabs[tab_name])
        self.tabs.clear()

        # Recreate tabs with controller
        self._create_tabs()