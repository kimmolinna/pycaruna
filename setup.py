import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycaruna",
    version="0.0.2",
    author="Sam Stenvall",
    author_email="neggelandia@gmail.com",
    description="Caruna API Python implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jalle19/pycaruna",
    project_urls={
        "Bug Tracker": "https://github.com/Jalle19/pycaruna/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2",
        "beautifulsoup4>=4.9",
        "lxml>=4.6"
    ]
)
