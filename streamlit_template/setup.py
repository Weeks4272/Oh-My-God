"""
GenomeAI setup configuration for package installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="genomeai",
    version="1.0.0",
    description="AI-powered genomics analysis pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GenomeAI Team",
    author_email="genomeai@example.com",
    url="https://github.com/genomeai/genomeai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="genomics bioinformatics ai machine-learning variant-calling rna-seq",
    entry_points={
        "console_scripts": [
            "genomeai=src.cli:app",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/genomeai/genomeai/issues",
        "Documentation": "https://docs.genomeai.org",
        "Source": "https://github.com/genomeai/genomeai",
    },
)