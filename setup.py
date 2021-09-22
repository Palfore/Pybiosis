import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pybiosis",
    version="0.0.6",
    author="Nawar Ismail",
    author_email="nawar@palfore.com",
    description="Python integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Palfore/Pybiosis",
    include_package_data=True,
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    # install_requires=[
    #     'pyautogui'
    # ]
)