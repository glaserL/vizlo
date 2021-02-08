import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vizlo",
    version="0.1.1",
    author="Luis Glaser",
    author_email="Luis.Glaser@uni-potsdam.de",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/glaserL/vizlo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "clingo>=5.4",
        "networkx>=2.4",
        "matplotlib>=3.2",
        "numpy>=1.16",
        "python-igraph>=0.8",
    ],
    test_suite="pytest",
    tests_require="pytest"
)
