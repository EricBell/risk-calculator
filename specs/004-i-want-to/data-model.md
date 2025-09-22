# Data Model: Qt Migration with Responsive Window Management

## Core Entities

### Window Configuration
**Purpose**: Stores user's preferred window dimensions, position, and display-specific settings
**Fields**:
- `width: int` - Window width in pixels (minimum 800)
- `height: int` - Window height in pixels (minimum 600)
- `x: int` - Window x position on screen
- `y: int` - Window y position on screen
- `maximized: bool` - Whether window is maximized
- `last_updated: datetime` - Timestamp of last configuration save

**Validation Rules**:
- Width must be >= 800 pixels
- Height must be >= 600 pixels
- Position coordinates must be within screen bounds
- Cannot be maximized if explicit dimensions provided

**State Transitions**:
- Created → Saved (when user resizes/moves window)
- Saved → Loaded (when application starts)
- Loaded → Validated (against current screen bounds)
- Validated → Applied (to Qt window)

### Display Profile
**Purpose**: Represents characteristics of the user's display for appropriate default sizing
**Fields**:
- `screen_width: int` - Available screen width
- `screen_height: int` - Available screen height
- `dpi_scale: float` - DPI scaling factor (1.0 = 100%, 2.0 = 200%)
- `is_high_dpi: bool` - Whether display is high-DPI
- `platform: str` - Operating system platform (Windows/Linux)

**Validation Rules**:
- Screen dimensions must be positive integers
- DPI scale must be between 0.5 and 4.0
- Platform must be in supported list

**Relationships**:
- One-to-one with Window Configuration (used for bounds validation)

### UI Layout State
**Purpose**: Tracks current scaling ratios and element positioning for proportional resizing
**Fields**:
- `base_width: int` - Original design width reference
- `base_height: int` - Original design height reference
- `current_width: int` - Current window width
- `current_height: int` - Current window height
- `scale_factor_x: float` - Horizontal scaling ratio
- `scale_factor_y: float` - Vertical scaling ratio
- `font_base_size: int` - Base font size for scaling calculations

**Validation Rules**:
- All dimensions must be positive integers
- Scale factors must be between 0.1 and 10.0
- Font base size must be between 8 and 72 points

**State Transitions**:
- Initialized → Calculated (when window size changes)
- Calculated → Applied (to UI elements)

## Data Flow

### Window Configuration Persistence
```
User Resize → Window Configuration Update → QSettings Storage → Home Directory File
Application Start → QSettings Load → Validation → Window Apply
```

### Responsive Scaling
```
Window Resize Event → Layout State Calculation → UI Element Scaling → Redraw
```

### High-DPI Handling
```
Application Start → Display Profile Detection → DPI Scale Factor → Global Qt Scaling
```

## Storage Schema

### QSettings Configuration Keys
```
window/width: int
window/height: int
window/x: int
window/y: int
window/maximized: bool
window/last_updated: string (ISO datetime)
```

### Platform Storage Locations
- **Windows**: `HKEY_CURRENT_USER\Software\RiskCalculator\`
- **Linux**: `~/.config/RiskCalculator/RiskCalculator.conf`

## Migration Considerations

### Existing Data Preservation
- All existing trade calculation models remain unchanged
- Risk calculation services maintain current interfaces
- Validation models continue to work with Qt UI components

### New Qt-Specific Models
- Window configuration models are new additions
- Display profile detection is framework-specific
- UI layout state replaces Tkinter-specific geometry management