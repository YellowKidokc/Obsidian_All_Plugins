"""
Setup script for Theophysics Backend
"""

from setuptools import setup, find_packages

with open("README_GITHUB.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="theophysics-backend",
    version="1.0.0",
    author="David Lowe",
    author_email="",
    description="Backend API for Theophysics research with definition processing and spiritual fruit data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YellowKidokc/LOWES-BACKEND-CLAUDE",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Religion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.3.0",
        "flask-cors>=4.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "gui": [
            "PySide6>=6.6.0",
        ],
        "ai": [
            "openai>=1.10.0",
            "anthropic>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "theophysics-cli=scripts.definition_cli:main",
            "theophysics-server=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md"],
    },
)
