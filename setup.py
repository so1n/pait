import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pait",
    version="0.4.1",
    author="so1n",
    author_email="so1n897046026@example.com",
    description="Pait is a python api interface tool, which can also be called a python api interface type (type hint)",
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
