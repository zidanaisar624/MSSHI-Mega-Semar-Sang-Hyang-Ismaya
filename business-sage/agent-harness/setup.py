from setuptools import setup

setup(
    name="cli-anything-business-sage",
    version="1.0.0",
    description="CLI-Anything Agent-Native Harness for Business Sage (S1 BBA -> S2 MBA -> Eternal Ph.D. Advisor)",
    packages=["cli_anything.business_sage"],
    entry_points={
        "console_scripts": [
            "cli-anything-business-sage=cli_anything.business_sage.cli_anything_business_sage:main",
            "business-sage=cli_anything.business_sage.cli_anything_business_sage:main",
        ]
    },
    python_requires=">=3.8",
)
