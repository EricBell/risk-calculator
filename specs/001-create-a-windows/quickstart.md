# Quickstart Guide: Windows Desktop Risk Calculator

## Prerequisites

### Development Environment
- **Visual Studio 2022** (Community, Professional, or Enterprise)
- **.NET 8.0 SDK** (included with Visual Studio 2022)
- **Windows 10 or later** for development and testing

### Verification Steps
```bash
# Verify .NET 8.0 installation
dotnet --version
# Should output: 8.0.x

# Verify Visual Studio workloads
# Ensure "Desktop development with .NET" workload is installed
```

## Project Setup (5 minutes)

### 1. Create New WPF Project
```bash
# Create solution directory
mkdir RiskCalculator.Desktop
cd RiskCalculator.Desktop

# Create WPF project
dotnet new wpf -n RiskCalculator.Desktop -f net8.0-windows

# Create test project
dotnet new nunit -n RiskCalculator.Desktop.Tests -f net8.0

# Add project reference
dotnet add RiskCalculator.Desktop.Tests reference RiskCalculator.Desktop

# Create solution file
dotnet new sln
dotnet sln add RiskCalculator.Desktop
dotnet sln add RiskCalculator.Desktop.Tests
```

### 2. Install Required Packages
```xml
<!-- RiskCalculator.Desktop.csproj -->
<PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.2" />
<PackageReference Include="System.ComponentModel.DataAnnotations" Version="8.0.0" />
```

```xml
<!-- RiskCalculator.Desktop.Tests.csproj -->
<PackageReference Include="Moq" Version="4.20.69" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
```

### 3. Project Structure Setup
```
RiskCalculator.Desktop/
├── Models/
├── ViewModels/
├── Views/
├── Services/
├── Validators/
└── Converters/
```

## Quick Implementation Test (10 minutes)

### 1. Create Basic Trade Model
```csharp
// Models/Trade.cs
using System.ComponentModel.DataAnnotations;
using CommunityToolkit.Mvvm.ComponentModel;

public abstract partial class Trade : ObservableObject
{
    [ObservableProperty]
    [Range(0.01, double.MaxValue, ErrorMessage = "Account size must be greater than $0")]
    private decimal accountSize;

    [ObservableProperty]
    [Range(1.0, 5.0, ErrorMessage = "Risk percentage must be between 1% and 5%")]
    private decimal riskPercentage = 2.0m;

    public decimal CalculatedRiskAmount => AccountSize * RiskPercentage / 100m;
}
```

### 2. Create Equity Trade Model
```csharp
// Models/EquityTrade.cs
using System.ComponentModel.DataAnnotations;
using CommunityToolkit.Mvvm.ComponentModel;

public partial class EquityTrade : Trade
{
    [ObservableProperty]
    [Required(ErrorMessage = "Symbol is required")]
    private string symbol = string.Empty;

    [ObservableProperty]
    [Range(0.01, double.MaxValue, ErrorMessage = "Entry price must be greater than $0")]
    private decimal entryPrice;

    [ObservableProperty]
    [Range(0.01, double.MaxValue, ErrorMessage = "Stop loss must be greater than $0")]
    private decimal stopLossPrice;

    public int CalculatedShares =>
        EntryPrice > StopLossPrice && EntryPrice > 0 && StopLossPrice > 0
            ? (int)(CalculatedRiskAmount / (EntryPrice - StopLossPrice))
            : 0;

    public decimal EstimatedRisk => CalculatedShares * (EntryPrice - StopLossPrice);
}
```

### 3. Create Basic View Model
```csharp
// ViewModels/EquityViewModel.cs
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class EquityViewModel : ObservableObject
{
    [ObservableProperty]
    private EquityTrade trade = new();

    [ObservableProperty]
    private string calculationResult = string.Empty;

    [RelayCommand(CanExecute = nameof(CanCalculate))]
    private void Calculate()
    {
        var shares = Trade.CalculatedShares;
        var risk = Trade.EstimatedRisk;
        CalculationResult = $"Shares: {shares:N0}, Risk: ${risk:N2}";
    }

    private bool CanCalculate() =>
        Trade.AccountSize > 0 &&
        Trade.EntryPrice > 0 &&
        Trade.StopLossPrice > 0 &&
        Trade.StopLossPrice < Trade.EntryPrice;

    [RelayCommand]
    private void Clear()
    {
        Trade = new EquityTrade();
        CalculationResult = string.Empty;
    }
}
```

### 4. Create Basic UI
```xml
<!-- Views/EquityTab.xaml -->
<UserControl x:Class="RiskCalculator.Desktop.Views.EquityTab">
    <Grid Margin="20">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="150"/>
            <ColumnDefinition Width="200"/>
        </Grid.ColumnDefinitions>

        <Label Grid.Row="0" Grid.Column="0" Content="Symbol:"/>
        <TextBox Grid.Row="0" Grid.Column="1" Text="{Binding Trade.Symbol, UpdateSourceTrigger=PropertyChanged}"/>

        <Label Grid.Row="1" Grid.Column="0" Content="Account Size:"/>
        <TextBox Grid.Row="1" Grid.Column="1" Text="{Binding Trade.AccountSize, UpdateSourceTrigger=PropertyChanged}"/>

        <Label Grid.Row="2" Grid.Column="0" Content="Risk %:"/>
        <TextBox Grid.Row="2" Grid.Column="1" Text="{Binding Trade.RiskPercentage, UpdateSourceTrigger=PropertyChanged}"/>

        <Label Grid.Row="3" Grid.Column="0" Content="Entry Price:"/>
        <TextBox Grid.Row="3" Grid.Column="1" Text="{Binding Trade.EntryPrice, UpdateSourceTrigger=PropertyChanged}"/>

        <Label Grid.Row="4" Grid.Column="0" Content="Stop Loss:"/>
        <TextBox Grid.Row="4" Grid.Column="1" Text="{Binding Trade.StopLossPrice, UpdateSourceTrigger=PropertyChanged}"/>

        <StackPanel Grid.Row="5" Grid.Column="0" Grid.ColumnSpan="2" Orientation="Horizontal" Margin="0,20,0,0">
            <Button Content="Calculate" Command="{Binding CalculateCommand}" Margin="0,0,10,0"/>
            <Button Content="Clear" Command="{Binding ClearCommand}"/>
        </StackPanel>

        <TextBlock Grid.Row="6" Grid.Column="0" Grid.ColumnSpan="2"
                   Text="{Binding CalculationResult}"
                   FontWeight="Bold" Margin="0,20,0,0"/>
    </Grid>
</UserControl>
```

## Acceptance Test Scenarios (15 minutes)

### Test Scenario 1: Basic Equity Calculation
**Given**: Application is running
**When**: User enters:
- Symbol: "AAPL"
- Account Size: $10,000
- Risk %: 2%
- Entry Price: $150
- Stop Loss: $145

**Then**:
- Calculate button becomes enabled
- Clicking Calculate shows: "Shares: 40, Risk: $200.00"

### Test Scenario 2: Input Validation
**Given**: Application is running
**When**: User enters stop loss ($155) higher than entry price ($150)
**Then**: Calculate button remains disabled

### Test Scenario 3: Clear Functionality
**Given**: User has entered data and calculated results
**When**: User clicks Clear button
**Then**: All fields reset to empty/default values

## Build and Run Instructions

### Development Build
```bash
# Build solution
dotnet build

# Run application
dotnet run --project RiskCalculator.Desktop

# Run tests
dotnet test
```

### Release Build
```bash
# Create release build
dotnet build -c Release

# Publish self-contained (includes .NET runtime)
dotnet publish -c Release -r win-x64 --self-contained

# Publish framework-dependent (requires .NET 8.0 installed)
dotnet publish -c Release -r win-x64 --no-self-contained
```

## Verification Checklist

### Functionality
- [ ] Application starts without errors
- [ ] Tabbed interface displays correctly
- [ ] Input validation provides immediate feedback
- [ ] Calculate button enables/disables appropriately
- [ ] Calculations produce expected results
- [ ] Clear button resets all inputs

### Performance
- [ ] Application startup < 3 seconds
- [ ] Calculations complete < 100ms
- [ ] Memory usage < 50MB
- [ ] UI remains responsive during calculations

### User Experience
- [ ] Tab switching preserves individual tab state
- [ ] Error messages are clear and actionable
- [ ] Results display is prominent and well-formatted
- [ ] Keyboard navigation works properly

## Next Steps

### Phase 2: Complete Implementation
1. Add Options and Futures tabs with similar UI
2. Implement proper validation service
3. Add comprehensive error handling
4. Create full test suite

### Phase 3: Polish and Testing
1. Add data annotations validation
2. Implement business rule validation
3. Add integration tests
4. Performance optimization

### Phase 4: Deployment
1. Create installer package
2. Add application icon and branding
3. Code signing for distribution
4. User documentation

## Troubleshooting

### Common Issues
1. **"Could not load file or assembly"**: Verify .NET 8.0 SDK installation
2. **WPF controls not appearing**: Check project targets `net8.0-windows`
3. **Binding not working**: Verify INotifyPropertyChanged implementation
4. **Commands not executing**: Check CanExecute logic and command binding

### Performance Issues
1. **Slow startup**: Check for heavy operations in constructors
2. **UI freezing**: Ensure calculations are not blocking UI thread
3. **Memory leaks**: Verify event handler cleanup and disposal patterns