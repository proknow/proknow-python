# ProKnow DS - Python SDK

The ProKnow DS - Python SDK library provides convenient access to the ProKnow API from applications written in the Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses.

## Documentation

Complete documentation is available on [Read the Docs](https://proknow-python.readthedocs.io/en/latest/).

## Development

### Mac OSX

Use the following steps if you need to be able to package the project to publish on PyPi or if you need to build the documentation.

1. Install the latest version of python. This will be installed alongside the version that your operating system provides.
2. Run the following to install/upgrade `pip`, `setuptools`, `wheel`, `twine`, `pipenv`.
```
python3 -m pip install --upgrade pip setuptools wheel twine pipenv
```
3. Initialize a virtual environment using `pipenv`.
```
pipenv install --dev
```
4. Activate the virtual environment using `pipenv shell`.

#### Packaging

First, make sure the version has been updated in setup.py. Then run the following outside your pipenv shell.

```
python3 setup.py bdist_wheel --universal
python3 -m twine upload dist/*
```

#### Testing

Before you start testing, you'll need access to a ProKnow DS organization where you can generate an [API token](https://support.proknow.com/article/165-configuring-your-profile#api-keys) for your project. Once you have your API token create a file called `pktestconfig.py` in the root of this project with the following contents:

```
#!/usr/bin/env python
base_url = "https://example.proknow.com"
credentials_id = "{{ id from credentials.json }}"
credentials_secret = "{{ secret from credentials.json }}"
```

Make sure to put your actual base_url and the id and secret from your `credentials.json` file in place of the placeholders above.

Next, run the tests with the `nox` command from within your pipenv shell.

```
nox
```

To run a specific test using python 3, use the following form:

```
pytest tests/{{file name}}::{{test name}}
```

To run tests with the HTML coverage report, use the following:

```
pytest --cov=proknow --cov-branch --cov-report html tests
```

#### Building the Documentation

With the pipenv shell, you can run `make clean && make html` to build the documentation.
```
pipenv shell
cd docs/
make clean && make html
```
