#!/usr/bin/env python3

from setuptools import setup

setup(
    name='mmc5883',
    version='0.0.1',
    description='mmc5883 driver',
    author='Blue Robotics',
    url='https://github.com/bluerobotics/mmc5883-python',
    packages=['mmc5883'],
    entry_points={
        'console_scripts': [
            'mmc5883-test=mmc5883.test:main',
            'mmc5883-report=mmc5883.report:main'
        ],
    },
    package_data={ "mmc5883": ["mmc5883.meta"]},
    install_requires=['smbus2'],
)
