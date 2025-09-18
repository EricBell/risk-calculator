# Quickstart Guide: Cross-Platform Desktop Risk Calculator

## Prerequisites

### Development Environment
- **Python 3.12+** (latest stable version recommended)
- **Any Python-compatible IDE** (VS Code, PyCharm, Sublime Text)
- **Windows 10+ or Linux** for development and testing

### Verification Steps
```bash
# Verify Python 3.12+ installation
python --version
# Should output: Python 3.12.x or higher

# Verify tkinter is available (should be included with Python)
python -c "import tkinter; print('Tkinter available')"

# Verify decimal module for financial calculations
python -c "import decimal; print('Decimal module available')"
```

## Project Setup (5 minutes)

### 1. Create Python Project Structure
```bash
# Create project directory
mkdir risk_calculator
cd risk_calculator

# Create Python package structure
mkdir models views controllers services tests

# Create __init__.py files for Python packages
touch __init__.py
touch models/__init__.py
touch views/__init__.py
touch controllers/__init__.py
touch services/__init__.py
touch tests/__init__.py

# Create main application entry point
touch main.py
```

### 2. Create Virtual Environment and Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install testing framework
pip install pytest pytest-mock

# Create requirements.txt (no external dependencies for core functionality)
echo "pytest>=7.0.0" > requirements.txt
echo "pytest-mock>=3.10.0" >> requirements.txt
```

### 3. Project Structure Setup
```
risk_calculator/
├── main.py                    # Application entry point
├── models/
│   ├── __init__.py
│   ├── trade.py              # Base trade model
│   ├── equity_trade.py       # Equity trade calculations
│   ├── option_trade.py       # Options trade calculations
│   └── future_trade.py       # Futures trade calculations
├── views/
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── equity_tab.py         # Equity trading tab
│   ├── option_tab.py         # Options trading tab
│   └── future_tab.py         # Futures trading tab
├── controllers/
│   ├── __init__.py
│   ├── main_controller.py    # Main application controller
│   └── calculation_controller.py  # Risk calculation logic
├── services/
│   ├── __init__.py
│   ├── risk_calculator.py    # Core risk calculation service
│   └── validators.py         # Input validation functions
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_calculations.py
    └── test_validators.py
```

## Quick Implementation Test (10 minutes)

### 1. Create Risk Method Enumeration
```python
# models/risk_method.py
from enum import Enum

class RiskMethod(Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    LEVEL_BASED = "level_based"
```

### 2. Create Basic Trade Model
```python
# models/trade.py
from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from .risk_method import RiskMethod

@dataclass
class Trade(ABC):
    account_size: Decimal = Decimal('0')
    risk_method: RiskMethod = RiskMethod.PERCENTAGE
    risk_percentage: Optional[Decimal] = Decimal('2.0')  # Default 2%
    fixed_risk_amount: Optional[Decimal] = None

    @property
    def calculated_risk_amount(self) -> Decimal:
        """Calculate risk amount based on selected method"""
        if self.risk_method == RiskMethod.PERCENTAGE:
            return self.account_size * self.risk_percentage / 100
        elif self.risk_method == RiskMethod.FIXED_AMOUNT:
            return self.fixed_risk_amount or Decimal('0')
        elif self.risk_method == RiskMethod.LEVEL_BASED:
            return self.account_size * Decimal('0.02')  # Default 2%
        return Decimal('0')

    @abstractmethod
    def calculate_position_size(self) -> int:
        """Calculate position size based on asset type and risk method"""
        pass
```

### 3. Create Equity Trade Model
```python
# models/equity_trade.py
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from .trade import Trade

@dataclass
class EquityTrade(Trade):
    symbol: str = ""
    entry_price: Decimal = Decimal('0')
    stop_loss_price: Optional[Decimal] = None  # For PERCENTAGE/FIXED_AMOUNT methods
    support_resistance_level: Optional[Decimal] = None  # For LEVEL_BASED method
    trade_direction: str = "LONG"  # LONG or SHORT

    def calculate_position_size(self) -> int:
        """Calculate number of shares based on risk method"""
        risk_per_share = self._get_risk_per_share()
        if risk_per_share <= 0:
            return 0

        shares = int(self.calculated_risk_amount / risk_per_share)
        return max(0, shares)

    def _get_risk_per_share(self) -> Decimal:
        """Calculate risk per share based on selected method"""
        if self.risk_method in [RiskMethod.PERCENTAGE, RiskMethod.FIXED_AMOUNT]:
            if self.stop_loss_price is None:
                return Decimal('0')
            return abs(self.entry_price - self.stop_loss_price)
        elif self.risk_method == RiskMethod.LEVEL_BASED:
            if self.support_resistance_level is None:
                return Decimal('0')
            return abs(self.entry_price - self.support_resistance_level)
        return Decimal('0')

    @property
    def estimated_risk(self) -> Decimal:
        """Actual risk amount for calculated position"""
        shares = self.calculate_position_size()
        risk_per_share = self._get_risk_per_share()
        return shares * risk_per_share
```

### 4. Create Basic Main Window
```python
# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from models.equity_trade import EquityTrade
from models.risk_method import RiskMethod

class RiskCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Risk Calculator")
        self.root.geometry("800x600")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_equity_tab()

    def create_equity_tab(self):
        """Create the equity trading tab with all three risk methods"""
        equity_frame = ttk.Frame(self.notebook)
        self.notebook.add(equity_frame, text="Equities")

        # Risk method selection
        method_frame = ttk.LabelFrame(equity_frame, text="Risk Method")
        method_frame.pack(fill=tk.X, padx=10, pady=5)

        self.risk_method_var = tk.StringVar(value=RiskMethod.PERCENTAGE.value)

        ttk.Radiobutton(method_frame, text="Percentage-based", variable=self.risk_method_var,
                       value=RiskMethod.PERCENTAGE.value, command=self.on_method_change).pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="Fixed Amount", variable=self.risk_method_var,
                       value=RiskMethod.FIXED_AMOUNT.value, command=self.on_method_change).pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="Level-based", variable=self.risk_method_var,
                       value=RiskMethod.LEVEL_BASED.value, command=self.on_method_change).pack(side=tk.LEFT)

        # Input fields
        input_frame = ttk.LabelFrame(equity_frame, text="Trade Details")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        # Common fields
        ttk.Label(input_frame, text="Symbol:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.symbol_var = tk.StringVar(value="AAPL")
        ttk.Entry(input_frame, textvariable=self.symbol_var).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Account Size ($):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.account_size_var = tk.StringVar(value="10000")
        ttk.Entry(input_frame, textvariable=self.account_size_var).grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Entry Price ($):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_price_var = tk.StringVar(value="150")
        ttk.Entry(input_frame, textvariable=self.entry_price_var).grid(row=2, column=1, padx=5, pady=2)

        # Method-specific fields (initially show percentage fields)
        self.create_method_fields(input_frame)

        # Buttons
        button_frame = ttk.Frame(equity_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)

        # Results
        result_frame = ttk.LabelFrame(equity_frame, text="Results")
        result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.result_text = tk.Text(result_frame, height=4, width=50)
        self.result_text.pack(padx=10, pady=10)

    def create_method_fields(self, parent):
        """Create method-specific input fields"""
        # Risk percentage field (for PERCENTAGE method)
        ttk.Label(parent, text="Risk Percentage (%):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.risk_percentage_var = tk.StringVar(value="2.0")
        self.risk_percentage_entry = ttk.Entry(parent, textvariable=self.risk_percentage_var)
        self.risk_percentage_entry.grid(row=3, column=1, padx=5, pady=2)

        # Fixed risk amount field (for FIXED_AMOUNT method)
        ttk.Label(parent, text="Fixed Risk Amount ($):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.fixed_risk_var = tk.StringVar(value="200")
        self.fixed_risk_entry = ttk.Entry(parent, textvariable=self.fixed_risk_var)
        self.fixed_risk_entry.grid(row=4, column=1, padx=5, pady=2)
        self.fixed_risk_entry.grid_remove()  # Initially hidden

        # Stop loss field (for PERCENTAGE/FIXED_AMOUNT methods)
        ttk.Label(parent, text="Stop Loss Price ($):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.stop_loss_var = tk.StringVar(value="145")
        self.stop_loss_entry = ttk.Entry(parent, textvariable=self.stop_loss_var)
        self.stop_loss_entry.grid(row=5, column=1, padx=5, pady=2)

        # Support/resistance level field (for LEVEL_BASED method)
        ttk.Label(parent, text="Support/Resistance ($):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.level_var = tk.StringVar(value="147")
        self.level_entry = ttk.Entry(parent, textvariable=self.level_var)
        self.level_entry.grid(row=6, column=1, padx=5, pady=2)
        self.level_entry.grid_remove()  # Initially hidden

    def on_method_change(self):
        """Handle risk method selection change"""
        method = RiskMethod(self.risk_method_var.get())

        # Hide all method-specific fields
        self.risk_percentage_entry.grid_remove()
        self.fixed_risk_entry.grid_remove()
        self.stop_loss_entry.grid_remove()
        self.level_entry.grid_remove()

        # Show relevant fields based on selected method
        if method == RiskMethod.PERCENTAGE:
            self.risk_percentage_entry.grid()
            self.stop_loss_entry.grid()
        elif method == RiskMethod.FIXED_AMOUNT:
            self.fixed_risk_entry.grid()
            self.stop_loss_entry.grid()
        elif method == RiskMethod.LEVEL_BASED:
            self.level_entry.grid()

    def calculate(self):
        """Calculate position size based on inputs and selected method"""
        try:
            # Create trade object
            trade = EquityTrade()
            trade.symbol = self.symbol_var.get()
            trade.account_size = Decimal(self.account_size_var.get())
            trade.entry_price = Decimal(self.entry_price_var.get())
            trade.risk_method = RiskMethod(self.risk_method_var.get())

            # Set method-specific fields
            if trade.risk_method == RiskMethod.PERCENTAGE:
                trade.risk_percentage = Decimal(self.risk_percentage_var.get())
                trade.stop_loss_price = Decimal(self.stop_loss_var.get())
            elif trade.risk_method == RiskMethod.FIXED_AMOUNT:
                trade.fixed_risk_amount = Decimal(self.fixed_risk_var.get())
                trade.stop_loss_price = Decimal(self.stop_loss_var.get())
            elif trade.risk_method == RiskMethod.LEVEL_BASED:
                trade.support_resistance_level = Decimal(self.level_var.get())

            # Calculate position size
            shares = trade.calculate_position_size()
            risk = trade.estimated_risk

            # Display results
            result = f"""
Method Used: {trade.risk_method.value.replace('_', ' ').title()}
Calculated Shares: {shares:,}
Estimated Risk: ${risk:.2f}
Risk Amount: ${trade.calculated_risk_amount:.2f}
"""
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result.strip())

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def clear(self):
        """Clear all input fields"""
        self.symbol_var.set("AAPL")
        self.account_size_var.set("10000")
        self.entry_price_var.set("150")
        self.risk_percentage_var.set("2.0")
        self.fixed_risk_var.set("200")
        self.stop_loss_var.set("145")
        self.level_var.set("147")
        self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RiskCalculatorApp(root)
    root.mainloop()
```

## Acceptance Test Scenarios (15 minutes)

### Test Scenario 1: Percentage-Based Equity Calculation
**Given**: Application is running with "Percentage-based" method selected
**When**: User enters:
- Symbol: "AAPL"
- Account Size: $10,000
- Risk %: 2%
- Entry Price: $150
- Stop Loss: $145

**Then**: Clicking Calculate shows:
- Method Used: Percentage
- Calculated Shares: 40
- Estimated Risk: $200.00
- Risk Amount: $200.00

### Test Scenario 2: Fixed Amount Risk Calculation
**Given**: Application is running
**When**: User selects "Fixed Amount" method and enters:
- Symbol: "AAPL"
- Account Size: $10,000
- Fixed Risk Amount: $50
- Entry Price: $100
- Stop Loss: $95

**Then**: Clicking Calculate shows:
- Method Used: Fixed Amount
- Calculated Shares: 10
- Estimated Risk: $50.00
- Risk Amount: $50.00

### Test Scenario 3: Level-Based Risk Calculation
**Given**: Application is running
**When**: User selects "Level-based" method and enters:
- Symbol: "AAPL"
- Account Size: $10,000
- Entry Price: $50
- Support/Resistance: $47

**Then**: Clicking Calculate shows:
- Method Used: Level Based
- Calculated Shares: 66
- Estimated Risk: $198.00
- Risk Amount: $200.00 (2% default)

### Test Scenario 4: Risk Method Switching
**Given**: User has data entered for percentage method
**When**: User switches to "Fixed Amount" method
**Then**: UI shows fixed amount field and hides percentage field, calculation clears

### Test Scenario 5: Clear Functionality
**Given**: User has entered data and calculated results
**When**: User clicks Clear button
**Then**: All fields reset to default values, results area clears

## Build and Run Instructions

### Development Run
```bash
# Navigate to project directory
cd risk_calculator

# Activate virtual environment (if created)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run the application directly
python main.py
```

### Testing
```bash
# Run unit tests
pytest tests/

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v tests/

# Run with coverage (if pytest-cov installed)
pytest --cov=models tests/
```

### Distribution Build
```bash
# Install PyInstaller for creating executable
pip install pyinstaller

# Create Windows executable (on Windows)
pyinstaller --onefile --windowed main.py

# Create Linux executable (on Linux)
pyinstaller --onefile --windowed main.py

# The executable will be in dist/ directory
```

## Verification Checklist

### Functionality
- [ ] Application starts without errors on Windows and Linux
- [ ] All three risk methods are available and functional
- [ ] Risk method switching shows/hides appropriate fields
- [ ] Percentage-based calculations work correctly (1-5% range)
- [ ] Fixed amount calculations work correctly ($10-$500 range)
- [ ] Level-based calculations work correctly with support/resistance
- [ ] Calculations produce expected results for all methods
- [ ] Clear button resets all inputs and preserves method selection
- [ ] Results display shows which method was used

### Performance
- [ ] Application startup < 3 seconds
- [ ] Calculations complete < 100ms regardless of method
- [ ] Memory usage < 50MB
- [ ] UI remains responsive during calculations
- [ ] Method switching is instantaneous

### User Experience
- [ ] Risk method radio buttons work correctly
- [ ] Method-specific fields appear/disappear properly
- [ ] Error handling works for invalid inputs
- [ ] Results display is clear and well-formatted
- [ ] Cross-platform UI looks consistent (Windows/Linux)

## Next Steps

### Phase 2: Complete Implementation
1. Add Options and Futures tabs with method-specific UI
2. Implement proper validation service with method-aware rules
3. Add comprehensive error handling for all risk methods
4. Create full test suite covering all three calculation methods
5. Implement MVC architecture separation

### Phase 3: Polish and Testing
1. Add input validation with method-specific error messages
2. Implement business rule validation for each risk method
3. Add integration tests for method switching scenarios
4. Performance optimization across all calculation methods
5. Cross-platform testing (Windows and Linux)

### Phase 4: Deployment
1. Create PyInstaller executable for both platforms
2. Add application icon and branding
3. Create installation packages (Windows MSI, Linux AppImage)
4. User documentation with risk method explanations

## Troubleshooting

### Common Issues
1. **"No module named 'tkinter'"**: Install tkinter package (usually included with Python)
2. **Import errors**: Verify all __init__.py files are created in directories
3. **Decimal import errors**: Ensure Python 3.12+ is being used
4. **Method switching not working**: Check RiskMethod enum values match UI

### Cross-Platform Issues
1. **Font rendering differences**: Test on both Windows and Linux
2. **Window sizing**: Verify layout works on different screen resolutions
3. **File path separators**: Use os.path.join() for cross-platform compatibility
4. **Executable creation**: Use platform-specific PyInstaller commands

### Performance Issues
1. **Slow startup**: Check for heavy imports in main.py
2. **UI freezing**: Ensure calculations use Decimal arithmetic efficiently
3. **Memory usage**: Profile with different risk methods and large numbers