import setuptools
from pybiosis.__version__ import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pybiosis",
    version=str(__version__),
    author="Nawar Ismail",
    author_email="nawar@palfore.com",
    description="Python Automation Software; Decorators as Entry-Points.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Palfore/Pybiosis",
    include_package_data=True,
    project_urls={
        "Bug Tracker": "https://github.com/Palfore/Pybiosis/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [  # TODO: Seems to bug. Possibly when chaining calls with these aliases.
            'pybiosis = pybiosis.__main__:main',
            'bb = pybiosis.__main__:main',  # TODO: make 'bb' dynamic with a CLI --alias command for config. Not sure if possible.
        ],
    },
)