from setuptools import setup, find_packages
from manheim_cloudmapper.version import VERSION, PROJECT_URL

with open('README.md') as f:
    long_description = f.read()

requires = [
    'boto3',
    'docutils>=0.10,<0.15',
    'tabulate>=0.8.0,<0.9.0',
    # for building generated policy docs
    'sphinx>=1.8.0,<1.9.0',
    'sphinx_rtd_theme',
    'pandas',
    'premailer'
]

setup(
    name='manheim-cloudmapper',
    version=VERSION,
    packages=find_packages(),
    install_requires=requires
)
