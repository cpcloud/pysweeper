"""PySweeper installation."""

import pathlib

from setuptools import setup

import versioneer

description = "Your favorite mine sweeping game, console style."

setup(
    name="pysweeper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/cpcloud/pysweeper",
    author="Phillip Cloud",
    author_email="cpcloud@gmail.com",
    maintainer="Phillip Cloud",
    maintainer_email="cpcloud@gmail.com",
    description=description,
    long_description=description,
    install_requires=(
        pathlib.Path(__file__)
        .parent.joinpath("requirements.txt")
        .read_text()
        .splitlines()
    ),
    python_requires=">=3.7",
    license="MIT",
    entry_points={"console_scripts": ["pysweeper = pysweeper.__main__:main"]},
)
