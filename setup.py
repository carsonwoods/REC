"""
Copyright 2020-2022 Carson Woods
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="runtime-environment-capture",
    version="0.2.1",
    author="Carson Woods",
    description="A wrapper to collect data for ensuring reproducibility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carsonwoods/rec",
    repository="https://github.com/carsonwoods/rec",
    documentation="https://github.com/carsonwoods/REC/wiki",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "rec=rec.__main__:main",
        ]
    },

)
