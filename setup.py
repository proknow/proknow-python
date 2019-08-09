import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proknow",
    version="0.10.0",
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
    install_requires=['six', 'requests>=2.18.0', 'futures'],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
)
