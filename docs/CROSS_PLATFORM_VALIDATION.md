# Cross-Platform Validation Guide

This document provides comprehensive validation procedures for the Qt Risk Calculator across Windows and Linux platforms.

## Prerequisites

### Windows Requirements
- Windows 10/11 (64-bit)
- Python 3.12+ with PySide6
- Display driver with DPI scaling support
- Administrator access for registry configuration testing

### Linux Requirements
- Modern Linux distribution (Ubuntu 20.04+, Fedora 35+, etc.)
- Python 3.12+ with PySide6
- X11 or Wayland display server
- XDG Base Directory support

## Validation Procedures

### Automated Validation

Run the automated cross-platform validation script:

```bash
# From project root
python scripts/cross_platform_validation.py
```

This script validates:
- Qt framework availability and version
- Display detection and DPI scaling
- Platform-specific configuration storage
- Window management capabilities
- Risk calculation accuracy preservation
- Application startup performance

### Manual Validation Checklist

#### Windows-Specific Testing

**1. High-DPI Display Support**
- [ ] Test on 125% DPI scaling (120 DPI)
- [ ] Test on 150% DPI scaling (144 DPI)
- [ ] Test on 200% DPI scaling (192 DPI)
- [ ] Verify UI elements scale properly
- [ ] Check font rendering quality

**2. Configuration Storage**
- [ ] Verify settings stored in Windows Registry
- [ ] Check `HKEY_CURRENT_USER\Software\RiskCalculator`
- [ ] Test configuration persistence across reboots
- [ ] Validate multi-user isolation

**3. Window Management**
- [ ] Test window positioning across multiple monitors
- [ ] Verify taskbar integration
- [ ] Check window state persistence (maximized/restored)
- [ ] Test window snapping behavior

**4. Performance Validation**
- [ ] Measure startup time (target: <3 seconds)
- [ ] Test UI responsiveness (target: <100ms)
- [ ] Monitor memory usage (target: <100MB)
- [ ] Check for memory leaks during extended use

#### Linux-Specific Testing

**1. Display Server Compatibility**
- [ ] Test on X11 display server
- [ ] Test on Wayland (if available)
- [ ] Verify HiDPI support
- [ ] Check fractional scaling (1.25x, 1.5x, 2x)

**2. Configuration Storage**
- [ ] Verify XDG Base Directory compliance
- [ ] Check config location: `~/.config/RiskCalculator/`
- [ ] Test with custom `XDG_CONFIG_HOME`
- [ ] Validate file permissions

**3. Desktop Integration**
- [ ] Test window manager integration (GNOME, KDE, XFCE)
- [ ] Verify desktop notifications (if implemented)
- [ ] Check application menu integration
- [ ] Test keyboard shortcuts

**4. Distribution Compatibility**
- [ ] Ubuntu/Debian-based distributions
- [ ] Fedora/Red Hat-based distributions
- [ ] Arch Linux
- [ ] openSUSE

### Platform-Specific Features

#### Windows Registry Configuration

```
HKEY_CURRENT_USER\Software\RiskCalculator\
├── window\
│   ├── width (DWORD)
│   ├── height (DWORD)
│   ├── x (DWORD)
│   ├── y (DWORD)
│   └── maximized (DWORD)
├── application\
│   ├── theme (String)
│   └── version (String)
└── calculation\
    ├── default_method (String)
    └── precision (DWORD)
```

#### Linux XDG Configuration

```
~/.config/RiskCalculator/
├── RiskCalculator.conf          # Main configuration file
└── backup/                      # Configuration backups
    └── RiskCalculator_backup_*.conf
```

### Expected Configuration Values

| Setting | Windows Registry | Linux Config File | Default Value |
|---------|------------------|-------------------|---------------|
| Window Width | `HKCU\Software\RiskCalculator\window\width` | `[window] width=` | 1024 |
| Window Height | `HKCU\Software\RiskCalculator\window\height` | `[window] height=` | 768 |
| DPI Scale | Auto-detected | Auto-detected | 1.0 |
| Theme | `HKCU\Software\RiskCalculator\application\theme` | `[application] theme=` | system |

## Validation Scenarios

### Scenario 1: Fresh Installation
1. Install on clean system
2. Run application for first time
3. Verify default window size and position
4. Check configuration creation
5. Test basic functionality

### Scenario 2: Configuration Migration
1. Create legacy configuration (if applicable)
2. Run new Qt application
3. Verify configuration migration
4. Test preserved settings
5. Validate new Qt-specific settings

### Scenario 3: Multi-Monitor Setup
1. Connect multiple monitors
2. Position window on secondary monitor
3. Disconnect/reconnect monitors
4. Verify window positioning recovery
5. Test DPI scaling across monitors

### Scenario 4: High-DPI Scaling
1. Change system DPI scaling
2. Restart application
3. Verify UI scaling adaptation
4. Test interaction responsiveness
5. Check font and image quality

### Scenario 5: Extended Usage Session
1. Run application for extended period (1+ hours)
2. Perform various calculations
3. Resize window multiple times
4. Switch between tabs frequently
5. Monitor memory usage for leaks

## Performance Benchmarks

### Startup Performance
- **Target**: <3 seconds total startup time
- **Measurement**: From process start to UI ready
- **Breakdown**:
  - Qt application creation: <500ms
  - Window initialization: <1 second
  - Configuration loading: <500ms
  - UI rendering: <1 second

### UI Responsiveness
- **Target**: <100ms response time
- **Tests**:
  - Button clicks: <50ms
  - Text input: <30ms
  - Tab switching: <100ms
  - Window resizing: <200ms
  - Menu operations: <100ms

### Memory Usage
- **Target**: <100MB total memory usage
- **Baseline**: <50MB after startup
- **Growth**: <10MB per hour of usage
- **Leak detection**: No growth after idle periods

## Troubleshooting Common Issues

### Windows Issues

**High-DPI Scaling Problems**
```bash
# Check if application is DPI-aware
dxdiag /t dxdiag_output.txt
# Look for DPI scaling information
```

**Registry Access Denied**
- Run as administrator for initial setup
- Check Windows User Account Control settings
- Verify user permissions

### Linux Issues

**Qt Platform Plugin Issues**
```bash
# Set Qt platform explicitly
export QT_QPA_PLATFORM=xcb  # For X11
export QT_QPA_PLATFORM=wayland  # For Wayland
```

**Configuration Directory Permissions**
```bash
# Fix permissions if needed
chmod 755 ~/.config/RiskCalculator/
chmod 644 ~/.config/RiskCalculator/*.conf
```

**Missing Qt Libraries**
```bash
# Ubuntu/Debian
sudo apt install python3-pyside6

# Fedora
sudo dnf install python3-pyside6

# Arch Linux
sudo pacman -S pyside6
```

## Validation Report Template

```markdown
# Cross-Platform Validation Report

**Platform**: [Windows/Linux]
**Version**: [OS Version]
**Date**: [YYYY-MM-DD]
**Tester**: [Name]

## Test Results

### Automated Tests
- [ ] Qt Availability: PASS/FAIL
- [ ] Display Detection: PASS/FAIL
- [ ] Configuration Storage: PASS/FAIL
- [ ] Window Management: PASS/FAIL
- [ ] Calculation Services: PASS/FAIL
- [ ] Application Startup: PASS/FAIL

### Manual Tests
- [ ] High-DPI Scaling: PASS/FAIL
- [ ] Multi-Monitor Support: PASS/FAIL
- [ ] Performance Benchmarks: PASS/FAIL
- [ ] Extended Usage: PASS/FAIL

### Platform-Specific
- [ ] Configuration Location: PASS/FAIL
- [ ] Desktop Integration: PASS/FAIL
- [ ] Permission Handling: PASS/FAIL

## Issues Found
[List any issues discovered]

## Recommendations
[Suggestions for improvements]
```

## Continuous Validation

### Automated Testing Pipeline
1. Run validation script on both platforms
2. Generate comparison reports
3. Monitor performance trends
4. Alert on regression detection

### Release Validation Checklist
- [ ] Windows 10 validation complete
- [ ] Windows 11 validation complete
- [ ] Ubuntu LTS validation complete
- [ ] Fedora latest validation complete
- [ ] Performance benchmarks met
- [ ] No critical issues found
- [ ] Documentation updated