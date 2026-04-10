"""Setup script for Weather Agent."""

from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent.resolve()

readme_path = BASE_DIR / "README.md"
requirements_path = BASE_DIR / "requirements.txt"

if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "AI-powered weather information agent"

requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

setup(
    name="weather-agent",
    version="1.0.0",
    author="Weather Agent Team",
    description="AI-powered weather information agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "weather-agent=src.cli:main",
        ],
    },
    include_package_data=True,
)
