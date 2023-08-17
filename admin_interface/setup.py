#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open("README.md").read()

setup(
    name="admin_interface",
    description="A frontend for the 1721 admin bot",
    author="1721 Tidal Force",
    author_email="concordroboticssteam@gmail.com",
    url="https://github.com/FRC-1721/AdminBot",
    packages=find_packages(include=["admin_interface"]),
    package_dir={"admin-interface": "admin_interface"},
    entry_points={
        "console_scripts": [
            "admin-interface=admin_interface.__main__:main",
        ],
    },
    python_requires=">=3.10.0",
    version="0.0.0",
    long_description=readme,
    include_package_data=True,
    install_requires=[
        "discord.py",
    ],
    license="MIT",
)
