import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pitch_perfect",
    version="0.0.1",
    author="Seyoung Park",
    author_email="seyoung.arts.park@protonmail.com",
    description="Pitch detector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=['bin/perfect', 'bin/perfect-transfer'],
    url="https://github.com/SuperShinyEyes/pitch-perfect",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
    ]
)