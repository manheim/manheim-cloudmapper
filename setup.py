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
    'sphinx_rtd_theme'
]

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: System :: Distributed Computing',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities'
]

setup(
    name='manheim-cloudmapper',
    version=VERSION,
    author='Manheim Release Engineering',
    author_email='man-releaseengineering@manheim.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='cloudmapper policy generation script and related utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requires,
    keywords="cloudmapper aws",
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'run-port-check = manheim_cloudmapper.run_port_check:main',
            'send-email = manheim_cloudmapper.send_email:main'
        ]
    }
)
