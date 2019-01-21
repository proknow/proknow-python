# ProKnow DS - Python SDK

The ProKnow DS - Python SDK library provides convenient access to the ProKnow API from applications written in the Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses.

## Development

### Mac OSX

Use the following steps if you need to be able to package the project to publish on PyPi or if you need to build the documentation.

1. Install the latest version of python. This will be installed alongside the version that your operating system provides.
2. Run the following to install/upgrade `pip`, `setuptools`, `wheel`, and `pipenv`.
```
python3 -m pip install --upgrade pip setuptools wheel pipenv
```
3. Initialize a virtual environment using `pipenv`.
```
pipenv install --dev
```
4. Activate the virtual environment using `pipenv shell`.

#### Packaging

First, make sure the version has been updated in setup.py. Then run the following.

```
python setup.py bdist_wheel --universal
twine upload dist/*
```

#### Building the Documentation

With the pipenv shell, you can run `make clean && make html` to build the documentation.
```
pipenv shell
cd docs/
make clean && make html
```
