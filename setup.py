import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pait",
    version="0.5.0",
    author="so1n",
    author_email="so1n897046026@gmail.com",
    description="Pait is a python api tool, which can also be called a python api type (type hint)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/so1n/pait",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
