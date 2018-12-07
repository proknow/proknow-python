import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proknow",
    version="0.0.1",
    author="ProKnow",
    author_email="support@proknow.com",
    description="Python library for the ProKnow API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/proknow/proknow-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
