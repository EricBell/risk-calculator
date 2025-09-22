# Qt Risk Calculator Deployment Guide

This guide provides comprehensive instructions for deploying the Qt-based Risk Calculator application across Windows and Linux platforms.

## Prerequisites

### System Requirements

#### Windows
- **OS**: Windows 10 (1903+) or Windows 11
- **Architecture**: x64 (64-bit)
- **Python**: 3.12+ (3.12.0 or later recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Display**: Any resolution, high-DPI displays fully supported
- **Graphics**: DirectX 11 compatible graphics adapter

#### Linux
- **OS**: Ubuntu 20.04 LTS+, Fedora 35+, or equivalent modern distribution
- **Architecture**: x86_64 (64-bit)
- **Python**: 3.12+ (3.12.0 or later recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Display**: X11 or Wayland display server
- **Graphics**: OpenGL 2.1+ compatible graphics adapter

### Python Dependencies

```
PySide6>=6.5.0
psutil>=5.9.0
pytest>=7.0.0 (for testing)
pytest-mock>=3.10.0 (for testing)
```

## Installation Methods

### Method 1: Source Installation (Recommended for Development)

1. **Clone Repository**
   ```bash
   git clone https://github.com/EricBell/risk-calculator.git
   cd risk-calculator
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python scripts/cross_platform_validation.py
   ```

5. **Run Application**
   ```bash
   python risk_calculator/qt_main.py
   ```

### Method 2: Standalone Executable (Recommended for End Users)

#### Windows Executable Creation

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Create Executable**
   ```bash
   pyinstaller --onefile --windowed \
     --name "RiskCalculator" \
     --icon "assets/icon.ico" \
     --add-data "risk_calculator;risk_calculator" \
     risk_calculator/qt_main.py
   ```

3. **Package for Distribution**
   ```bash
   # Creates installer using NSIS or similar
   # See Windows Packaging section below
   ```

#### Linux AppImage Creation

1. **Install AppImage Tools**
   ```bash
   # Ubuntu/Debian
   sudo apt install appimage-builder

   # Fedora
   sudo dnf install appimage-builder
   ```

2. **Create AppImage**
   ```bash
   appimage-builder --recipe appimage-builder.yml
   ```

3. **Make Executable**
   ```bash
   chmod +x RiskCalculator-*.AppImage
   ```

## Configuration Management

### Windows Configuration
- **Storage**: Windows Registry (`HKEY_CURRENT_USER\Software\RiskCalculator`)
- **Location**: Automatically managed by QSettings
- **Backup**: Registry export recommended before major updates

### Linux Configuration
- **Storage**: XDG Base Directory (`~/.config/RiskCalculator/`)
- **Format**: INI-style configuration files
- **Backup**: Copy `~/.config/RiskCalculator/` directory

### Configuration Migration
The application automatically migrates settings from previous versions:
1. Detects existing configuration
2. Validates format and version
3. Migrates to new format if needed
4. Creates backup of original settings

## Platform-Specific Deployment

### Windows Deployment

#### MSI Installer Creation

1. **Install WiX Toolset**
   ```bash
   # Download from https://wixtoolset.org/
   # Or use Chocolatey:
   choco install wixtoolset
   ```

2. **Create Installer Script** (`risk-calculator.wxs`)
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
     <Product Id="*" Name="Risk Calculator" Language="1033"
              Version="1.0.0" Manufacturer="YourCompany"
              UpgradeCode="PUT-GUID-HERE">
       <Package InstallerVersion="200" Compressed="yes" InstallScope="perUser" />

       <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
       <MediaTemplate EmbedCab="yes" />

       <Feature Id="ProductFeature" Title="Risk Calculator" Level="1">
         <ComponentGroupRef Id="ProductComponents" />
       </Feature>
     </Product>

     <Fragment>
       <Directory Id="TARGETDIR" Name="SourceDir">
         <Directory Id="LocalAppDataFolder">
           <Directory Id="INSTALLFOLDER" Name="Risk Calculator" />
         </Directory>
       </Directory>
     </Fragment>

     <Fragment>
       <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
         <Component Id="ProductComponent">
           <File Source="dist/RiskCalculator.exe" />
         </Component>
       </ComponentGroup>
     </Fragment>
   </Wix>
   ```

3. **Build Installer**
   ```bash
   candle risk-calculator.wxs
   light risk-calculator.wixobj
   ```

#### Windows Store Packaging (Optional)

1. **Create MSIX Package**
   ```bash
   # Use Visual Studio or MakeAppx.exe
   makeappx pack /d PackageFiles /p RiskCalculator.msix
   ```

2. **Sign Package**
   ```bash
   signtool sign /fd SHA256 /a RiskCalculator.msix
   ```

### Linux Deployment

#### .deb Package Creation (Ubuntu/Debian)

1. **Create Debian Package Structure**
   ```
   risk-calculator_1.0.0/
   ├── DEBIAN/
   │   ├── control
   │   ├── postinst
   │   └── prerm
   └── usr/
       ├── bin/
       │   └── risk-calculator
       ├── share/
       │   ├── applications/
       │   │   └── risk-calculator.desktop
       │   └── icons/
       │       └── hicolor/
       │           └── 256x256/
       │               └── apps/
       │                   └── risk-calculator.png
       └── local/
           └── lib/
               └── risk-calculator/
   ```

2. **Create Control File** (`DEBIAN/control`)
   ```
   Package: risk-calculator
   Version: 1.0.0
   Section: office
   Priority: optional
   Architecture: amd64
   Depends: python3 (>= 3.12), python3-pyside6
   Maintainer: Your Name <your.email@example.com>
   Description: Professional daytrading risk calculator
    Cross-platform desktop application for calculating position sizes
    across equities, options, and futures based on account risk tolerance.
   ```

3. **Build Package**
   ```bash
   dpkg-deb --build risk-calculator_1.0.0
   ```

#### .rpm Package Creation (Fedora/RHEL)

1. **Create RPM Spec File** (`risk-calculator.spec`)
   ```spec
   Name:           risk-calculator
   Version:        1.0.0
   Release:        1%{?dist}
   Summary:        Professional daytrading risk calculator

   License:        MIT
   URL:            https://github.com/EricBell/risk-calculator
   Source0:        %{name}-%{version}.tar.gz

   BuildRequires:  python3-devel
   Requires:       python3 >= 3.12, python3-pyside6

   %description
   Cross-platform desktop application for calculating position sizes
   across equities, options, and futures based on account risk tolerance.

   %files
   %{_bindir}/risk-calculator
   %{_datadir}/applications/risk-calculator.desktop
   %{_datadir}/icons/hicolor/256x256/apps/risk-calculator.png
   ```

2. **Build RPM**
   ```bash
   rpmbuild -ba risk-calculator.spec
   ```

#### Flatpak Package Creation

1. **Create Flatpak Manifest** (`com.yourcompany.RiskCalculator.json`)
   ```json
   {
     "app-id": "com.yourcompany.RiskCalculator",
     "runtime": "org.kde.Platform",
     "runtime-version": "6.5",
     "sdk": "org.kde.Sdk",
     "command": "risk-calculator",
     "finish-args": [
       "--share=ipc",
       "--socket=x11",
       "--socket=wayland",
       "--filesystem=home"
     ],
     "modules": [
       {
         "name": "risk-calculator",
         "buildsystem": "simple",
         "build-commands": [
           "pip3 install --prefix=/app ."
         ],
         "sources": [
           {
             "type": "dir",
             "path": "."
           }
         ]
       }
     ]
   }
   ```

2. **Build Flatpak**
   ```bash
   flatpak-builder build-dir com.yourcompany.RiskCalculator.json
   ```

## Performance Optimization

### Application Optimization

1. **Startup Optimization**
   ```python
   # In qt_main.py, implement lazy loading
   def create_main_window(self):
       # Load heavy components on demand
       window = QtMainWindow()
       window.lazy_load_tabs()
       return window
   ```

2. **Memory Optimization**
   ```python
   # Implement memory management
   def cleanup_unused_resources(self):
       # Clear caches, remove unused objects
       gc.collect()
   ```

3. **Display Optimization**
   ```python
   # Enable high-DPI optimization
   QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
   QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
   ```

### System-Level Optimization

#### Windows
```batch
# Set high-DPI awareness in registry
reg add "HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" /v "C:\Path\To\RiskCalculator.exe" /t REG_SZ /d "HIGHDPIAWARE" /f
```

#### Linux
```bash
# Set environment variables for optimal performance
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1.0
```

## Testing and Validation

### Pre-Deployment Testing

1. **Functional Testing**
   ```bash
   # Run comprehensive test suite
   pytest tests/ -v --tb=short

   # Run performance tests
   pytest tests/performance/ -v --tb=short
   ```

2. **Cross-Platform Validation**
   ```bash
   # Run platform-specific validation
   python scripts/cross_platform_validation.py
   ```

3. **Load Testing**
   ```bash
   # Test with extended usage simulation
   python tests/performance/test_memory.py::TestMemoryUsageValidation::test_long_running_session_memory_stability
   ```

### Post-Deployment Monitoring

1. **Error Tracking**
   - Implement application logging
   - Monitor crash reports
   - Track performance metrics

2. **User Feedback Collection**
   - In-app feedback mechanism
   - Usage analytics (privacy-compliant)
   - Performance monitoring

## Deployment Environments

### Development Environment
```bash
# Quick development setup
git clone <repo>
cd risk-calculator
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python risk_calculator/qt_main.py
```

### Staging Environment
```bash
# Production-like testing environment
# Use containerized deployment for consistency
docker build -t risk-calculator:staging .
docker run -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=:0 risk-calculator:staging
```

### Production Environment
```bash
# Full deployment with monitoring
# Install via package manager (deb/rpm/msi)
sudo apt install ./risk-calculator_1.0.0_amd64.deb  # Linux
# or run MSI installer on Windows
```

## Security Considerations

### Application Security
- **Code Signing**: Sign executables with valid certificates
- **Input Validation**: Robust validation of all user inputs
- **Configuration Security**: Encrypt sensitive configuration data
- **Update Mechanism**: Secure update delivery and verification

### Platform Security

#### Windows
- **SmartScreen**: Ensure executable passes Windows SmartScreen
- **Antivirus**: Test with major antivirus software
- **UAC**: Minimize UAC prompts, run as standard user

#### Linux
- **AppArmor/SELinux**: Create security profiles if needed
- **File Permissions**: Set appropriate permissions for config files
- **Sandboxing**: Consider Flatpak for additional sandboxing

## Troubleshooting

### Common Issues

#### Qt Platform Plugin Issues
```bash
# Error: qt.qpa.plugin: Could not load the Qt platform plugin
export QT_QPA_PLATFORM=xcb  # Linux X11
export QT_QPA_PLATFORM=wayland  # Linux Wayland
# On Windows, ensure Qt DLLs are in PATH
```

#### High-DPI Display Issues
```bash
# Force DPI scaling if auto-detection fails
export QT_SCALE_FACTOR=1.5  # Linux
# Windows: Use display settings or compatibility mode
```

#### Configuration Access Issues
```bash
# Linux: Fix config directory permissions
chmod 755 ~/.config/RiskCalculator/
chmod 644 ~/.config/RiskCalculator/*.conf

# Windows: Reset registry permissions if needed
# Use regedit.exe with administrator privileges
```

### Performance Issues

#### Slow Startup
1. Check for missing Qt libraries
2. Verify Python environment setup
3. Test with minimal configuration
4. Check display driver issues

#### High Memory Usage
1. Monitor with task manager/htop
2. Check for memory leaks in calculation loops
3. Verify configuration size
4. Test with default settings

## Maintenance and Updates

### Update Strategy
1. **Automated Updates**: Implement secure update mechanism
2. **Rollback Plan**: Maintain ability to rollback to previous version
3. **Configuration Migration**: Handle configuration format changes
4. **Data Preservation**: Ensure user data is preserved during updates

### Long-term Maintenance
1. **Dependency Updates**: Regular updates of Qt and Python dependencies
2. **Platform Compatibility**: Test on new OS versions
3. **Performance Monitoring**: Track performance metrics over time
4. **User Feedback**: Regular collection and analysis of user feedback

## Support and Documentation

### User Documentation
- Installation guides for each platform
- User manual with screenshots
- FAQ and troubleshooting guide
- Video tutorials for common tasks

### Developer Documentation
- API documentation
- Architecture overview
- Contributing guidelines
- Development environment setup

### Support Channels
- GitHub Issues for bug reports
- Documentation wiki
- Community forums (if applicable)
- Professional support (if commercial)

---

## Quick Reference

### Essential Commands
```bash
# Install and run
pip install -r requirements.txt
python risk_calculator/qt_main.py

# Test installation
python scripts/cross_platform_validation.py

# Run test suite
pytest tests/ -v

# Create executable
pyinstaller --onefile --windowed risk_calculator/qt_main.py

# Package for distribution
# See platform-specific sections above
```

### Configuration Locations
- **Windows**: Registry `HKCU\Software\RiskCalculator`
- **Linux**: `~/.config/RiskCalculator/RiskCalculator.conf`

### Performance Targets
- **Startup Time**: <3 seconds
- **UI Response**: <100ms
- **Memory Usage**: <100MB
- **Cross-Platform**: Windows 10+ and modern Linux distributions