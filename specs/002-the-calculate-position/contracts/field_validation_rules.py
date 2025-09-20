"""
Contract: Field Validation Rules
Purpose: Define validation rules and requirements for each field type
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from decimal import Decimal
from dataclasses import dataclass


@dataclass 
class ValidationRule:
    """A single validation rule for a field."""
    field_name: str
    rule_type: str  # "required", "positive", "range", "relationship"
    parameters: Dict[str, Any]
    error_message: str


@dataclass
class FieldRequirement:
    """Requirements for a specific field in a calculation context."""
    field_name: str
    is_required: bool
    validation_rules: List[ValidationRule]
    tab_types: List[str]  # Which tabs use this field
    methods: List[str]    # Which methods require this field


class IFieldValidationRules(ABC):
    """Interface defining field validation rules across all tabs."""
    
    @abstractmethod
    def get_field_requirements(self, field_name: str) -> FieldRequirement:
        """
        Get validation requirements for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            FieldRequirement defining validation rules
            
        Raises:
            KeyError: If field_name is not recognized
        """
        pass
    
    @abstractmethod
    def validate_field_value(self, field_name: str, value: str, 
                           context: Dict[str, Any]) -> Optional[str]:
        """
        Validate a field value against its rules.
        
        Args:
            field_name: Name of the field
            value: Field value to validate
            context: Additional validation context (other field values, method, etc.)
            
        Returns:
            Error message if invalid, None if valid
        """
        pass


# Field validation rule definitions

EQUITY_FIELD_RULES = {
    "account_size": FieldRequirement(
        field_name="account_size",
        is_required=True,
        validation_rules=[
            ValidationRule("account_size", "required", {}, "Account size is required"),
            ValidationRule("account_size", "positive", {"min_value": "0.01"}, 
                         "Account size must be greater than $0.01"),
            ValidationRule("account_size", "range", {"max_value": "10000000", "warning": True},
                         "Warning: Account size over $10M is unusual")
        ],
        tab_types=["equity", "options", "futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "symbol": FieldRequirement(
        field_name="symbol",
        is_required=True,
        validation_rules=[
            ValidationRule("symbol", "required", {}, "Symbol is required"),
            ValidationRule("symbol", "length", {"max_length": 10}, 
                         "Symbol must be 10 characters or less")
        ],
        tab_types=["equity"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "entry_price": FieldRequirement(
        field_name="entry_price",
        is_required=True,
        validation_rules=[
            ValidationRule("entry_price", "required", {}, "Entry price is required"),
            ValidationRule("entry_price", "positive", {"min_value": "0.01"},
                         "Entry price must be greater than $0.01"),
            ValidationRule("entry_price", "range", {"max_value": "10000", "warning": True},
                         "Warning: Entry price over $10,000 is unusual")
        ],
        tab_types=["equity", "futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "risk_percentage": FieldRequirement(
        field_name="risk_percentage",
        is_required=True,
        validation_rules=[
            ValidationRule("risk_percentage", "required", {}, "Risk percentage is required"),
            ValidationRule("risk_percentage", "range", {"min_value": "1.0", "max_value": "5.0"},
                         "Risk percentage must be between 1.0% and 5.0%")
        ],
        tab_types=["equity", "options", "futures"],
        methods=["percentage"]
    ),
    
    "stop_loss_price": FieldRequirement(
        field_name="stop_loss_price",
        is_required=True,
        validation_rules=[
            ValidationRule("stop_loss_price", "required", {}, "Stop loss price is required"),
            ValidationRule("stop_loss_price", "positive", {"min_value": "0.01"},
                         "Stop loss price must be greater than $0.01"),
            ValidationRule("stop_loss_price", "relationship", 
                         {"depends_on": "entry_price", "trade_direction": "trade_direction"},
                         "Stop loss must be below entry price for LONG, above for SHORT")
        ],
        tab_types=["equity", "futures"],
        methods=["percentage", "fixed_amount"]
    ),
    
    "fixed_risk_amount": FieldRequirement(
        field_name="fixed_risk_amount",
        is_required=True,
        validation_rules=[
            ValidationRule("fixed_risk_amount", "required", {}, "Fixed risk amount is required"),
            ValidationRule("fixed_risk_amount", "range", {"min_value": "10", "max_value": "500"},
                         "Fixed risk amount must be between $10 and $500"),
            ValidationRule("fixed_risk_amount", "relationship",
                         {"depends_on": "account_size", "max_percent": "5"},
                         "Fixed risk amount cannot exceed 5% of account size")
        ],
        tab_types=["equity", "options", "futures"],
        methods=["fixed_amount"]
    ),
    
    "support_resistance_level": FieldRequirement(
        field_name="support_resistance_level",
        is_required=True,
        validation_rules=[
            ValidationRule("support_resistance_level", "required", {}, 
                         "Support/resistance level is required"),
            ValidationRule("support_resistance_level", "positive", {"min_value": "0.01"},
                         "Support/resistance level must be greater than $0.01"),
            ValidationRule("support_resistance_level", "relationship",
                         {"depends_on": "entry_price", "trade_direction": "trade_direction"},
                         "Support level must be below entry for LONG, resistance above for SHORT")
        ],
        tab_types=["equity", "futures"],
        methods=["level_based"]
    )
}

OPTIONS_FIELD_RULES = {
    "option_symbol": FieldRequirement(
        field_name="option_symbol",
        is_required=True,
        validation_rules=[
            ValidationRule("option_symbol", "required", {}, "Option symbol is required")
        ],
        tab_types=["options"],
        methods=["percentage", "fixed_amount"]
    ),
    
    "premium": FieldRequirement(
        field_name="premium",
        is_required=True,
        validation_rules=[
            ValidationRule("premium", "required", {}, "Premium is required"),
            ValidationRule("premium", "positive", {"min_value": "0.01"},
                         "Premium must be greater than $0.01"),
            ValidationRule("premium", "range", {"max_value": "1000", "warning": True},
                         "Warning: Premium over $1,000 is unusual")
        ],
        tab_types=["options"],
        methods=["percentage", "fixed_amount"]
    ),
    
    "contract_multiplier": FieldRequirement(
        field_name="contract_multiplier",
        is_required=True,
        validation_rules=[
            ValidationRule("contract_multiplier", "required", {}, "Contract multiplier is required"),
            ValidationRule("contract_multiplier", "positive", {"min_value": "1"},
                         "Contract multiplier must be greater than 0"),
            ValidationRule("contract_multiplier", "range", {"expected_value": "100", "warning": True},
                         "Warning: Contract multiplier is usually 100")
        ],
        tab_types=["options"],
        methods=["percentage", "fixed_amount"]
    )
}

FUTURES_FIELD_RULES = {
    "contract_symbol": FieldRequirement(
        field_name="contract_symbol",
        is_required=True,
        validation_rules=[
            ValidationRule("contract_symbol", "required", {}, "Contract symbol is required")
        ],
        tab_types=["futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "tick_value": FieldRequirement(
        field_name="tick_value",
        is_required=True,
        validation_rules=[
            ValidationRule("tick_value", "required", {}, "Tick value is required"),
            ValidationRule("tick_value", "positive", {"min_value": "0.01"},
                         "Tick value must be greater than $0.01")
        ],
        tab_types=["futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "tick_size": FieldRequirement(
        field_name="tick_size",
        is_required=True,
        validation_rules=[
            ValidationRule("tick_size", "required", {}, "Tick size is required"),
            ValidationRule("tick_size", "positive", {"min_value": "0.01"},
                         "Tick size must be greater than $0.01")
        ],
        tab_types=["futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    ),
    
    "margin_requirement": FieldRequirement(
        field_name="margin_requirement",
        is_required=True,
        validation_rules=[
            ValidationRule("margin_requirement", "required", {}, "Margin requirement is required"),
            ValidationRule("margin_requirement", "positive", {"min_value": "0.01"},
                         "Margin requirement must be greater than $0.01"),
            ValidationRule("margin_requirement", "relationship",
                         {"depends_on": "account_size", "max_percent": "100"},
                         "Margin requirement cannot exceed account size")
        ],
        tab_types=["futures"],
        methods=["percentage", "fixed_amount", "level_based"]
    )
}

# Method support by tab
METHOD_SUPPORT = {
    "equity": ["percentage", "fixed_amount", "level_based"],
    "options": ["percentage", "fixed_amount"],  # level_based NOT supported
    "futures": ["percentage", "fixed_amount", "level_based"]
}

# Required fields by method and tab
REQUIRED_FIELDS_BY_METHOD = {
    ("equity", "percentage"): [
        "account_size", "symbol", "entry_price", "trade_direction", 
        "risk_percentage", "stop_loss_price"
    ],
    ("equity", "fixed_amount"): [
        "account_size", "symbol", "entry_price", "trade_direction",
        "fixed_risk_amount", "stop_loss_price"
    ],
    ("equity", "level_based"): [
        "account_size", "symbol", "entry_price", "trade_direction",
        "support_resistance_level"
    ],
    ("options", "percentage"): [
        "account_size", "option_symbol", "premium", "contract_multiplier",
        "trade_direction", "risk_percentage"
    ],
    ("options", "fixed_amount"): [
        "account_size", "option_symbol", "premium", "contract_multiplier",
        "trade_direction", "fixed_risk_amount"
    ],
    ("futures", "percentage"): [
        "account_size", "contract_symbol", "entry_price", "tick_value",
        "tick_size", "margin_requirement", "trade_direction",
        "risk_percentage", "stop_loss_price"
    ],
    ("futures", "fixed_amount"): [
        "account_size", "contract_symbol", "entry_price", "tick_value",
        "tick_size", "margin_requirement", "trade_direction",
        "fixed_risk_amount", "stop_loss_price"
    ],
    ("futures", "level_based"): [
        "account_size", "contract_symbol", "entry_price", "tick_value",
        "tick_size", "margin_requirement", "trade_direction",
        "support_resistance_level"
    ]
}