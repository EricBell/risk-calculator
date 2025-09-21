# Quickstart: UI Bug Fixes and Window Responsiveness

**Feature**: UI Bug Fixes and Window Responsiveness
**Branch**: `003-there-are-several`
**Date**: 2025-09-20

## Overview

This quickstart guide provides step-by-step instructions to verify that all UI bugs have been fixed and window responsiveness features are working correctly.

## Prerequisites

- Risk Calculator application built and running
- Test data available for all trade types (equity, options, futures)
- Multiple screen resolution test environments (recommended: 1920x1080 and 3840x2160)

## Test Scenarios

### 1. Calculate Position Button Functionality

#### Scenario 1A: Button Enablement with Valid Data
**Purpose**: Verify button becomes enabled when all required fields contain valid data

**Steps**:
1. Launch the Risk Calculator application
2. Navigate to the Equity tab
3. Enter the following valid data:
   - Account Size: `10000`
   - Risk Percentage: `2`
   - Entry Price: `50.00`
   - Stop Loss: `48.00`
4. Observe the Calculate Position button state

**Expected Result**: Button should be enabled (not grayed out) and clickable

#### Scenario 1B: Button Execution
**Purpose**: Verify button executes calculation when clicked

**Steps**:
1. Continue from Scenario 1A (button should be enabled)
2. Click the "Calculate Position" button
3. Observe the calculation results area

**Expected Result**: Position calculation should execute and display result (e.g., "200 shares")

#### Scenario 1C: Button Disabled with Invalid Data
**Purpose**: Verify button becomes disabled when required fields are empty or invalid

**Steps**:
1. Clear the Entry Price field (leave empty)
2. Observe the Calculate Position button state

**Expected Result**: Button should be disabled (grayed out) and not clickable

### 2. Error Message Display

#### Scenario 2A: Field-Specific Error Messages
**Purpose**: Verify clear error messages appear near problematic fields

**Steps**:
1. Navigate to the Options tab
2. Enter invalid data:
   - Account Size: `abc` (invalid - should be numeric)
   - Premium: `-5` (invalid - should be positive)
3. Click in another field to trigger validation

**Expected Result**:
- Error message should appear near Account Size field: "Account size must be a positive number"
- Error message should appear near Premium field: "Premium must be greater than 0"

#### Scenario 2B: Error Message Visibility During Resize
**Purpose**: Verify error messages remain visible when window is resized

**Steps**:
1. Continue from Scenario 2A (error messages should be visible)
2. Resize the window to a smaller size (1024x600)
3. Resize the window to a larger size (1600x1000)

**Expected Result**: Error messages should remain visible and properly positioned during all resize operations

### 3. Menu Item Functionality

#### Scenario 3A: Calculate Position Menu with Valid Data
**Purpose**: Verify menu item executes calculation when form data is valid

**Steps**:
1. Navigate to the Futures tab
2. Enter valid data:
   - Account Size: `25000`
   - Risk Percentage: `1.5`
   - Entry Price: `4200`
   - Stop Loss: `4150`
   - Tick Value: `12.50`
3. Use menu: Actions → Calculate Position

**Expected Result**: Calculation should execute and display result

#### Scenario 3B: Calculate Position Menu with Invalid Data
**Purpose**: Verify menu item shows validation errors when form data is invalid

**Steps**:
1. Clear the Tick Value field (leave empty)
2. Use menu: Actions → Calculate Position

**Expected Result**: Validation error dialog should appear explaining "Tick Value is required for futures calculations"

### 4. Window Responsiveness

#### Scenario 4A: Window Resizing with Layout Preservation
**Purpose**: Verify UI elements scale properly during window resize

**Steps**:
1. Start with default window size
2. Gradually resize window larger (drag corner to ~1600x1200)
3. Gradually resize window smaller (drag corner to ~900x700)
4. Observe layout of all UI elements during resize

**Expected Result**:
- All UI elements should remain proportionally sized
- No elements should disappear or overlap
- Layout should remain usable at all sizes
- Resize operations should be smooth (no lag or flickering)

#### Scenario 4B: Minimum Size Constraint
**Purpose**: Verify window cannot be resized below minimum usable size

**Steps**:
1. Attempt to resize window smaller than 800x600
2. Try dragging window borders to very small dimensions

**Expected Result**: Window should not resize below 800x600 pixels

#### Scenario 4C: High DPI Display Compatibility
**Purpose**: Verify application works correctly on high-resolution displays

**Steps** (requires high DPI display):
1. Run application on 4K display (3840x2160) with scaling
2. Verify default window size is appropriate
3. Test all resize operations

**Expected Result**:
- Application should be usable without being too small
- All text should be readable
- UI elements should be appropriately sized

### 5. Window Configuration Persistence

#### Scenario 5A: Window State Persistence
**Purpose**: Verify window size and position are saved and restored

**Steps**:
1. Resize window to custom size (e.g., 1400x900)
2. Move window to specific position on screen
3. Close the application completely
4. Reopen the application
5. Observe window size and position

**Expected Result**: Window should open at the same size and position as when it was closed

#### Scenario 5B: Invalid Configuration Recovery
**Purpose**: Verify application recovers gracefully from invalid saved window settings

**Steps**:
1. Close the application
2. Navigate to `~/.risk_calculator/` directory
3. Edit `window_config.json` to have invalid values:
   ```json
   {
     "window": {
       "width": 50000,
       "height": 50000,
       "x": -10000,
       "y": -10000,
       "maximized": false
     }
   }
   ```
4. Reopen the application

**Expected Result**: Application should open with reasonable default size (80% of screen, centered) and recreate valid configuration

#### Scenario 5C: Missing Configuration File
**Purpose**: Verify application creates configuration when file is missing

**Steps**:
1. Close the application
2. Delete `~/.risk_calculator/window_config.json` file
3. Reopen the application

**Expected Result**: Application should open with default window size (1024x768) and create new configuration file

### 6. Cross-Platform Compatibility

#### Scenario 6A: Windows Platform Verification
**Purpose**: Verify all features work correctly on Windows 10+

**Prerequisites**: Windows 10 or Windows 11 system

**Steps**:
1. Execute all previous scenarios on Windows platform
2. Verify configuration file is created in correct Windows home directory
3. Test window snapping and Windows-specific behaviors

**Expected Result**: All scenarios should pass identically to Linux

#### Scenario 6B: Linux Platform Verification
**Purpose**: Verify all features work correctly on Linux desktop environments

**Prerequisites**: Linux system with desktop environment (GNOME, KDE, XFCE, etc.)

**Steps**:
1. Execute all previous scenarios on Linux platform
2. Verify configuration file is created in `~/.risk_calculator/`
3. Test with different window managers if available

**Expected Result**: All scenarios should pass identically to Windows

## Performance Verification

### Response Time Testing
**Purpose**: Verify UI remains responsive during all operations

**Method**:
- All button state changes should occur within 100ms of field changes
- Window resize operations should maintain 60fps smoothness
- Error message display/hide should be instantaneous
- Application startup should remain under 3 seconds

### Memory Usage Testing
**Purpose**: Verify new features don't significantly impact memory usage

**Method**:
- Monitor memory usage before and after implementing features
- Memory increase should be less than 5MB
- No memory leaks during extended window resize operations

## Success Criteria

### Functional Success
- [ ] All Calculate Position button scenarios pass
- [ ] All error message display scenarios pass
- [ ] All menu item functionality scenarios pass
- [ ] All window responsiveness scenarios pass
- [ ] All configuration persistence scenarios pass
- [ ] All cross-platform compatibility scenarios pass

### Performance Success
- [ ] UI responsiveness maintained under 100ms
- [ ] Window resize operations smooth at 60fps
- [ ] Memory usage increase under 5MB
- [ ] Application startup time unchanged

### Quality Success
- [ ] No regression in existing functionality
- [ ] All existing tests continue to pass
- [ ] Cross-platform behavior identical
- [ ] Error messages are clear and helpful

## Troubleshooting

### Common Issues and Solutions

**Issue**: Button remains disabled despite valid data
**Solution**: Check console/logs for validation errors; verify all required fields for current risk method are filled

**Issue**: Error messages not appearing
**Solution**: Verify error label widgets are properly configured and not hidden by layout manager

**Issue**: Window configuration not persisting
**Solution**: Check file permissions for `~/.risk_calculator/` directory; verify JSON format is valid

**Issue**: Poor resize performance
**Solution**: Check for expensive operations in resize event handlers; verify grid weights are properly configured

**Issue**: Window opens off-screen
**Solution**: Delete configuration file to reset to defaults; check multi-monitor setup

## Manual Verification Checklist

Before considering the feature complete, manually verify:

- [ ] Calculate Position button correctly enabled/disabled in all tabs
- [ ] Button click executes calculation in all tabs
- [ ] Menu Calculate Position works in all tabs
- [ ] Error messages appear for all invalid field types
- [ ] Error messages clear when fields become valid
- [ ] Window resizes smoothly in all directions
- [ ] Minimum size constraints enforced
- [ ] Window state persists across application restarts
- [ ] Configuration corruption handled gracefully
- [ ] Works identically on Windows and Linux
- [ ] High DPI displays properly supported
- [ ] No regression in existing calculation functionality