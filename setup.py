"""Setup configuration for RFGhost package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="rfghost",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="RF signal monitoring and anomaly detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/RFGhost",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rfghost=rfghost.main:main",
        ],
    },
) 