#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open("README.md").read()

setup(
    name="admin_bot",
    description="A custom discord bot for mannaging the tidal force discord server.",
    author="1721 Tidal Force",
    author_email="concordroboticssteam@gmail.com",
    url="https://github.com/FRC-1721/AdminBot",
    packages=find_packages(include=["admin_bot"]),
    package_dir={"admin-bot": "admin_bot"},
    entry_points={
        "console_scripts": [
            "admin-bot=admin_bot.__main__:main",
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
