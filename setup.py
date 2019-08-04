"""PySweeper installation."""

import pathlib

from setuptools import setup

import versioneer

setup(
    name="pysweeper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Phillip Cloud",
    author_email="cpcloud@gmail.com",
    description="Your favorite mine sweeping game, console style.",
    install_requires=(
        pathlib.Path(__file__)
        .parent.joinpath("requirements.txt")
        .read_text()
        .splitlines()
    ),
    python_requires=">=3.7",
    license="MIT",
    entry_points={"console_scripts": ["pysweep = pysweeper.console:main"]},
)
