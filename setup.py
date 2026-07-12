from setuptools import setup, find_packages

setup(
    name="sdr-scanner",
    version="1.0.0",
    author="janderik",
    description="SDR Security Testing Toolkit",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={"console_scripts": ["sdr-scanner=cli:main"]},
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License"],
)
