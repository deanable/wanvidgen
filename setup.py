"""
setup.py for WanVidGen package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from file
def read_requirements():
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "customtkinter>=5.2.0",
        "Pillow>=9.0.0",
    ]

setup(
    name="wanvidgen",
    version="0.1.0",
    description="A CustomTkinter GUI application for video generation",
    long_description=Path("README.md").read_text() if Path("README.md").exists() else "",
    long_description_content_type="text/markdown",
    author="WanVidGen Team",
    author_email="team@wanvidgen.com",
    url="https://github.com/your-org/wanvidgen",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "wanvidgen=wanvidgen.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
    package_data={
        "wanvidgen": ["*.json", "*.yaml", "*.yml"],
    },
)