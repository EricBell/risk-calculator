# Quickstart: Qt Migration with Responsive Window Management

## Prerequisites
- Python 3.12+ installed
- PySide6 library installed (`pip install PySide6`)
- Existing risk calculator codebase available

## Setup
```bash
# Install Qt dependencies
pip install PySide6

# Verify Qt installation
python -c "from PySide6.QtWidgets import QApplication; print('Qt installation successful')"
```

## Testing Scenarios

### Scenario 1: First Launch High-DPI Display
**Objective**: Verify application adapts to high-resolution displays

1. Launch application on high-DPI display (>150% scaling)
2. **Expected**: Window opens at appropriate size for display resolution
3. **Expected**: All UI elements are clearly readable without manual adjustment
4. **Expected**: No configuration file exists yet in user home directory

**Validation**:
- Window dimensions are proportional to screen size
- Text and buttons are appropriately sized for readability
- No pixelated or tiny UI elements

### Scenario 2: Window Resize and Persistence
**Objective**: Verify responsive scaling and configuration saving

1. From Scenario 1, resize window to preferred dimensions
2. Move window to different screen position
3. **Expected**: All UI elements scale proportionally during resize
4. **Expected**: Form fields, labels, and buttons maintain relative sizes
5. Close application
6. **Expected**: Configuration file created in user home directory
7. Restart application
8. **Expected**: Window opens at previously saved size and position

**Validation**:
- UI elements scale smoothly during resize
- No layout breakage or overlapping elements
- Window state persists between sessions

### Scenario 3: Risk Calculation Preservation
**Objective**: Verify all existing calculations work identically

1. Switch to Equity tab
2. Enter test data: Account Size: 10000, Risk %: 2, Entry: 50, Stop Loss: 48
3. Click Calculate Position
4. **Expected**: Result shows 250 shares (identical to Tkinter version)
5. Switch to Options tab
6. Enter test data: Account Size: 10000, Risk %: 2, Premium: 2.50, Multiplier: 100
7. Click Calculate Position
8. **Expected**: Result shows 8 contracts (identical to Tkinter version)

**Validation**:
- Calculation results match existing Tkinter implementation exactly
- All three risk methods (percentage, fixed, level-based) work correctly
- Input validation behaves identically

### Scenario 4: Cross-Platform Configuration
**Objective**: Verify configuration works across Windows and Linux

1. On Windows: Configure window size and close application
2. **Expected**: Configuration saved to Windows Registry or AppData
3. On Linux: Launch application with fresh configuration
4. **Expected**: Uses Linux-appropriate default size for display
5. Configure different window size on Linux
6. **Expected**: Configuration saved to ~/.config/ directory

**Validation**:
- Each platform uses appropriate configuration storage
- Default sizes adapt to platform display characteristics
- No cross-platform configuration conflicts

### Scenario 5: Edge Case Handling
**Objective**: Verify graceful handling of configuration issues

1. Create invalid configuration file with impossible dimensions
2. Launch application
3. **Expected**: Falls back to safe default window size
4. Disconnect external monitor (if using multi-monitor setup)
5. Launch application
6. **Expected**: Window appears on primary display with valid coordinates

**Validation**:
- Application never crashes due to configuration issues
- Always provides usable window dimensions
- Handles missing or corrupted configuration gracefully

## Performance Validation

### Startup Time
- Application must start within 3 seconds on target hardware
- Qt initialization should be faster than previous Tkinter version

### Responsiveness
- Window resize operations must render at 60fps on supported hardware
- UI element scaling should complete within 100ms of resize event
- Calculate button response time must remain under 100ms

### Memory Usage
- Application memory usage must remain under 100MB during normal operation
- No memory leaks during window resize operations

## Success Criteria

All scenarios must pass with the following outcomes:
- ✅ High-DPI displays show appropriately sized UI elements
- ✅ Window configuration persists between application sessions
- ✅ All existing risk calculations produce identical results
- ✅ UI elements scale proportionally during window resize
- ✅ Cross-platform configuration works on Windows and Linux
- ✅ Application handles configuration edge cases gracefully
- ✅ Performance meets constitutional requirements

## Regression Testing

Before release, verify:
- All existing unit tests continue to pass
- Business logic calculations remain unchanged
- Input validation behaviors are preserved
- Platform-specific features work correctly

## Troubleshooting

### Common Issues
- **Qt not found**: Ensure PySide6 is installed in correct Python environment
- **High-DPI issues**: Verify Qt.AA_EnableHighDpiScaling is set before QApplication creation
- **Configuration not saving**: Check user home directory write permissions
- **Window off-screen**: Delete configuration file to reset to defaults