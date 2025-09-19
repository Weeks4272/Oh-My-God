#!/usr/bin/env python3
"""
Setup script for AI Engine Python Implementation
Provides installation and configuration for the Python AI engine
"""

from setuptools import setup, find_packages
import sys
import os

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read README for long description
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "AI Engine - Python Implementation for Code Generation and Analysis"

setup(
    name="ai-engine",
    version="1.0.0",
    author="AI Engine Team",
    author_email="ai-engine@example.com",
    description="Real AI Engine with Python and C++ for code generation and analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ai-engine/ai-engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "gpu": [
            "torch[cuda]>=2.0.0",
            "tensorflow[gpu]>=2.13.0",
        ],
        "full": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "tensorflow>=2.13.0",
            "openai>=0.27.0",
            "onnxruntime-gpu>=1.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-engine=ai_engine:main",
            "ai-engine-server=ai_engine:run_server",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_engine": [
            "models/*.json",
            "templates/*.txt",
            "config/*.yaml",
        ],
    },
)