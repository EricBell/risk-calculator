# Risk Calculator - Cross-Platform Desktop Application

A professional desktop application for daytrading position sizing calculations, built with Python and Qt6.

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- Qt6 framework (PySide6)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd risk-calculator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # OR install with setup.py:
   pip install -e .
   ```

3. **Run the application:**
   ```bash
   # Recommended: Qt-based version
   python -m risk_calculator.qt_main

   # OR if installed via setup.py:
   risk-calculator
   ```

### Qt Dependencies Installation

The application requires PySide6 (Qt6 for Python). Install it using:

```bash
pip install PySide6>=6.5.0
```

For development with additional monitoring capabilities:
```bash
pip install psutil>=5.9.0
```

## 📋 Features

### Risk Calculation Methods
- **Percentage Risk**: Calculate position size based on account percentage risk
- **Fixed Amount Risk**: Calculate position size based on fixed dollar amount risk
- **Level-based Risk**: Calculate position size based on price level differences

### Trading Instruments
- **Equities**: Stock position sizing with entry/stop loss prices
- **Options**: Contract sizing based on premium and risk amount
- **Futures**: Contract sizing with tick value and tick risk calculations

### Technical Capabilities
- **Cross-Platform**: Windows and Linux support
- **High-DPI Ready**: Automatic scaling for 4K displays and high-DPI monitors
- **Responsive UI**: Smart window resizing and multi-monitor support
- **Persistent Settings**: Window state and configuration saved across sessions
- **Real-time Validation**: Instant feedback and error highlighting
- **Performance Optimized**: <3s startup, <100ms UI response, <100MB memory usage

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 10+ or Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.12 or higher
- **Memory**: 256MB RAM
- **Display**: 1024x768 resolution

### Recommended Requirements
- **OS**: Windows 11 or Linux (Ubuntu 20.04+)
- **Python**: 3.12+
- **Memory**: 512MB RAM
- **Display**: 1920x1080 or higher (supports 4K/high-DPI)

## 🔧 Development Setup

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/          # Unit tests
python -m pytest tests/integration/   # Integration tests
python -m pytest tests/contract/      # Contract tests
python -m pytest tests/performance/   # Performance tests

# Run with coverage
python -m pytest tests/ --cov=risk_calculator
```

### Development Mode
```bash
# Run with debug logging
python -m risk_calculator.qt_main --debug

# Run with performance monitoring
python -m risk_calculator.qt_main --performance
```

## 📖 Usage Examples

### Basic Position Sizing (Equities)
1. Select "Equity" tab
2. Enter account size: $10,000
3. Select "Percentage" risk method
4. Enter risk percentage: 2%
5. Enter entry price: $50.00
6. Enter stop loss: $48.00
7. Click "Calculate Position" → Shows number of shares to buy

### Options Position Sizing
1. Select "Options" tab
2. Enter account size: $10,000
3. Enter risk amount: $200
4. Enter option premium: $2.50
5. Click "Calculate Position" → Shows number of contracts

### Futures Position Sizing
1. Select "Futures" tab
2. Enter account size: $25,000
3. Enter risk amount: $500
4. Enter tick value: $12.50
5. Enter ticks at risk: 8
6. Click "Calculate Position" → Shows number of contracts

## ⚠️ Migration from Tkinter Version

**The Tkinter version is now DEPRECATED.** Please migrate to the Qt version:

### Old (Deprecated):
```bash
python -m risk_calculator.main_tkinter_deprecated
# OR
risk-calculator-tkinter
```

### New (Recommended):
```bash
python -m risk_calculator.qt_main
# OR
risk-calculator
```

**Why migrate to Qt?**
- Better cross-platform support
- High-DPI display compatibility
- Enhanced user interface
- Improved performance and reliability
- Modern UI widgets and styling
- Better window management

## 🏗️ Architecture

### Project Structure
```
risk_calculator/
├── qt_main.py                 # Qt application entry point
├── main_tkinter_deprecated.py # Deprecated Tkinter entry point
├── models/                    # Data models and configuration
├── views/                     # UI components (Qt + legacy Tkinter)
├── controllers/               # Application controllers
├── services/                  # Business logic and services
└── tests/                     # Comprehensive test suite
```

### Technology Stack
- **Language**: Python 3.12+
- **UI Framework**: Qt6 (PySide6)
- **Architecture**: MVC with separation of concerns
- **Testing**: pytest with Qt testing framework
- **Performance**: psutil monitoring
- **Packaging**: PyInstaller for distribution

## 🐛 Troubleshooting

### Common Issues

**Qt Installation Problems:**
```bash
# Update pip first
pip install --upgrade pip

# Install Qt dependencies
pip install PySide6>=6.5.0

# Linux: Install Qt system dependencies
sudo apt-get install qt6-base-dev  # Ubuntu/Debian
sudo yum install qt6-qtbase-devel  # RHEL/CentOS
```

**High-DPI Display Issues:**
- Qt automatically handles high-DPI scaling
- Ensure PySide6 version is 6.5.0 or higher
- Check display scaling settings in your OS

**Application Won't Start:**
```bash
# Check Python version
python --version  # Should be 3.12+

# Verify Qt installation
python -c "from PySide6.QtWidgets import QApplication; print('Qt OK')"

# Run with debug output
python -m risk_calculator.qt_main --debug
```

### Performance Issues
- Ensure you have sufficient RAM (512MB recommended)
- Close unnecessary applications
- Check system requirements above

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]

## 📞 Support

[Add support/contact information here]

---

**Version**: 1.0.0
**Last Updated**: September 2025
**Python Version**: 3.12+
**Qt Version**: 6.5.0+