from setuptools import setup, find_packages

setup(
    name="amazon_keyword_tool",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0",
        "scikit-learn>=1.3",
        "numpy>=1.24",
        "playwright>=1.40",
        "beautifulsoup4>=4.12",
        "lxml>=4.9",
    ],
    extras_require={
        "dev": ["pytest>=8.0", "pytest-cov"],
    },
)
