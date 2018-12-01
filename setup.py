# coding=UTF-8

"""
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

# Possibly convert the README.md to .rst-format
try:
    import pypandoc
    README = pypandoc.convert('README.md', 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    README = open('README.md', 'r').read()


setup(
    name='nrkdownload',

    # Version number is automatically extracted from Git
    # https://pypi.python.org/pypi/setuptools_scm
    # https://packaging.python.org/en/latest/single_source_version.html
    use_scm_version={'write_to': 'src/nrkdownload/version.py'},

    setup_requires=['setuptools_scm', 'pypandoc'],
    # tests_require=['pytest', 'pytest-cov'],

    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['requests', 'requests_cache', 'tqdm', 'future',
                      'python-dateutil'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
       'testing': ['pytest', 'pytest-cov', 'pytest-console-scripts'],
    },

    description='Download series or programs from NRK, '
                'complete with images and subtitles',
    long_description=README,

    # The project's main homepage.
    url='https://github.com/marhoy/nrk-download',

    # Author details
    author='Martin Høy',
    author_email='martin.hoy@pvv.ntnu.no',

    # Choose your license
    license='GPL3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Topic :: Multimedia :: Video',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # What does your project relate to?
    keywords='download video',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # packages=['src/nrkdownload'],
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # exclude_package_data={'': ['API-testing.ipynb']},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'nrkdownload=nrkdownload.commandline_script:main',
        ]
    },
)
