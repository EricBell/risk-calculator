# View Model Contracts

## Base View Model Contract

### Interface: IBaseViewModel
```csharp
public interface IBaseViewModel : INotifyPropertyChanged
{
    bool IsBusy { get; }
    bool HasErrors { get; }
    ValidationResult ValidationResult { get; }
}
```

**Property Contracts**:
- `IsBusy`: True during calculation operations, false otherwise
- `HasErrors`: True when validation fails, false when all inputs valid
- `ValidationResult`: Current validation state with error messages

**Event Contracts**:
- `PropertyChanged`: Raised when any property value changes
- Must provide property name for UI binding updates

## Equity View Model Contract

### Interface: IEquityViewModel : IBaseViewModel
```csharp
public interface IEquityViewModel : IBaseViewModel
{
    EquityTrade Trade { get; set; }
    CalculationResult CalculationResult { get; }
    ICommand CalculateCommand { get; }
    ICommand ClearCommand { get; }
}
```

**Property Contracts**:
- `Trade`: Current equity trade data with validation
- `CalculationResult`: Result of last calculation attempt
- All changes to Trade properties trigger validation

**Command Contracts**:

#### CalculateCommand
- **CanExecute**: Returns true when Trade is valid and not busy
- **Execute**:
  1. Sets IsBusy = true
  2. Validates Trade inputs
  3. Calls risk calculation service
  4. Updates CalculationResult
  5. Sets IsBusy = false
- **Execution Time**: < 100ms for all calculations

#### ClearCommand
- **CanExecute**: Always returns true
- **Execute**:
  1. Resets all Trade properties to default values
  2. Clears ValidationResult
  3. Clears CalculationResult
  4. Triggers PropertyChanged for all affected properties

**Validation Behavior**:
- Real-time validation on property changes
- Error indicators update immediately
- Calculate button disabled when validation fails

## Option View Model Contract

### Interface: IOptionViewModel : IBaseViewModel
```csharp
public interface IOptionViewModel : IBaseViewModel
{
    OptionTrade Trade { get; set; }
    CalculationResult CalculationResult { get; }
    ICommand CalculateCommand { get; }
    ICommand ClearCommand { get; }
}
```

**Behavior**: Same as EquityViewModel but operates on OptionTrade data

**Specific Validation**:
- ContractMultiplier defaults to 100
- Premium validation for reasonable option values
- Risk calculation based on total premium cost

## Future View Model Contract

### Interface: IFutureViewModel : IBaseViewModel
```csharp
public interface IFutureViewModel : IBaseViewModel
{
    FutureTrade Trade { get; set; }
    CalculationResult CalculationResult { get; }
    ICommand CalculateCommand { get; }
    ICommand ClearCommand { get; }
}
```

**Behavior**: Same as EquityViewModel but operates on FutureTrade data

**Specific Validation**:
- Tick size and tick value coordinate validation
- Margin requirement vs. account size warnings
- Complex risk calculation with multiple parameters

## Main View Model Contract

### Interface: IMainViewModel : INotifyPropertyChanged
```csharp
public interface IMainViewModel : INotifyPropertyChanged
{
    int SelectedTabIndex { get; set; }
    IEquityViewModel EquityViewModel { get; }
    IOptionViewModel OptionViewModel { get; }
    IFutureViewModel FutureViewModel { get; }
}
```

**Property Contracts**:
- `SelectedTabIndex`: 0=Equities, 1=Options, 2=Futures
- Individual view models maintain independent state
- Tab switching preserves individual tab data

**Behavior Contracts**:
- Tab switching does not clear other tab data
- Each tab view model operates independently
- No cross-tab data sharing or validation

## UI Binding Contracts

### Input Field Bindings
```xml
<!-- Text input with validation -->
<TextBox Text="{Binding Trade.EntryPrice, UpdateSourceTrigger=PropertyChanged,
                ValidatesOnDataErrors=True, NotifyOnValidationError=True}" />

<!-- Error display -->
<TextBlock Text="{Binding ValidationResult.ErrorMessages[0]}"
           Visibility="{Binding HasErrors, Converter={StaticResource BoolToVisibilityConverter}}" />

<!-- Calculate button -->
<Button Content="Calculate" Command="{Binding CalculateCommand}"
        IsEnabled="{Binding CalculateCommand.CanExecute}" />
```

**Binding Requirements**:
- `UpdateSourceTrigger=PropertyChanged` for real-time validation
- `ValidatesOnDataErrors=True` for built-in validation support
- Error message display with proper visibility binding
- Command binding with CanExecute state management

### Result Display Bindings
```xml
<!-- Calculation results -->
<TextBlock Text="{Binding CalculationResult.PositionSize, StringFormat='{0:N0} shares'}"
           Visibility="{Binding CalculationResult.IsSuccess, Converter={StaticResource BoolToVisibilityConverter}}" />

<TextBlock Text="{Binding CalculationResult.EstimatedRisk, StringFormat='${0:N2}'}"
           Visibility="{Binding CalculationResult.IsSuccess, Converter={StaticResource BoolToVisibilityConverter}}" />

<!-- Error display -->
<TextBlock Text="{Binding CalculationResult.ErrorMessage}"
           Foreground="Red"
           Visibility="{Binding CalculationResult.IsSuccess, Converter={StaticResource InverseBoolToVisibilityConverter}}" />
```

**Display Requirements**:
- Conditional visibility based on calculation success
- Proper formatting for numeric results
- Error messages in distinguishable color/style
- Clear visual hierarchy for results vs. errors

## Testing Contracts

### View Model Unit Tests
Each view model must test:
1. **Property change notifications**: Verify PropertyChanged events
2. **Command execution**: Test CanExecute and Execute behavior
3. **Validation triggering**: Ensure validation runs on property changes
4. **Error state management**: Verify HasErrors updates correctly
5. **Calculation integration**: Mock service calls and verify results

### Integration Test Requirements
1. **UI binding tests**: Verify property changes update UI
2. **Command binding tests**: Ensure buttons enable/disable correctly
3. **Validation display tests**: Check error messages appear properly
4. **Tab switching tests**: Verify state preservation across tabs

### Performance Requirements
- Property change notifications: < 1ms per property
- Validation execution: < 10ms per validation run
- UI update responsiveness: < 16ms for smooth 60fps experience
- Memory leak prevention: No retained references after tab switches