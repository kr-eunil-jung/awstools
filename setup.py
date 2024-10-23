from setuptools import setup, find_packages
from awstools import __version__

setup(
    name='awstools',
    version=__version__,
    description='AWS Library',
    url='https://github.com/kr-eunil-jung/awstools',
    author='Eunil Jung',
    author_email='happy89322@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'numpy',
        'tqdm',
        'redis',
        'fastapi'
    ],
    entry_points={
        'console_scripts': [
            'awstools=awstools:main'
        ]
    }
)