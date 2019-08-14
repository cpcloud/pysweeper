"""PySweeper installation."""

import pathlib

from setuptools import setup

import versioneer

directory = pathlib.Path(__file__).parent

setup(
    name="pysweeper",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://github.com/cpcloud/pysweeper",
    author="Phillip Cloud",
    author_email="cpcloud@gmail.com",
    maintainer="Phillip Cloud",
    maintainer_email="cpcloud@gmail.com",
    description="Your favorite mine sweeping game, console style.",
    long_description=directory.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    install_requires=(
        directory.joinpath("requirements.txt").read_text().splitlines()
    ),
    python_requires=">=3.7",
    license="MIT",
    entry_points={"console_scripts": ["pysweeper = pysweeper.__main__:main"]},
)
