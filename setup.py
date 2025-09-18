from setuptools import setup, find_packages

setup(
    name="risk-calculator",
    version="1.0.0",
    description="Cross-platform desktop risk calculator for daytrading",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        # No external dependencies - using Python standard library only
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "risk-calculator=risk_calculator.main:main",
        ],
    },
)