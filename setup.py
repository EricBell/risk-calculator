from setuptools import setup, find_packages

setup(
    name="risk-calculator",
    version="1.0.0",
    description="Cross-platform desktop risk calculator for daytrading",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "PySide6>=6.5.0",  # Qt6 framework for Python
        "psutil>=5.9.0",   # Performance monitoring
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "risk-calculator=risk_calculator.qt_main:main",
            "risk-calculator-tkinter=risk_calculator.main_tkinter_deprecated:main",  # Deprecated
        ],
    },
)