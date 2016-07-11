from __future__ import absolute_import, division, print_function

from setuptools import setup
import versioneer

setup(
    name='pysweeper',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Phillip Cloud',
    author_email='cpcloud@gmail.com',
    description='Your favorite mine sweeping game -- console style',
    install_requires=[],
    license='BSD',
    entry_points={
        'console_scripts': ['pysweeper = pysweeper.console:main']
    }
)
