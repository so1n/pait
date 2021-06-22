import setuptools  # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pait",
    version="0.5.8",
    author="so1n",
    author_email="so1n897046026@gmail.com",
    description=(
        "Pait is a Python api tool. Pait enables your Python web framework to have type checking,"
        " parameter type conversion, interface document generation and can display your documents "
        "through Redoc or Swagger (power by inspect, pydantic)"
    ),
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
