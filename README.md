# ProKnow DS - Python SDK

The ProKnow DS - Python SDK library provides convenient access to the ProKnow API from applications written in the Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses.

## Documentation

Complete documentation is available on [Read the Docs](https://proknow-python.readthedocs.io/en/latest/).

## Development

### Mac OSX

#### Initializing a Development Environment

1. Install the latest version of Python. This will be installed alongside the version that your operating system provides.
2. Run the following.
```sh
$ python3 -m venv env
$ source env/bin/activate
(env) $ pip install --upgrade pip
(env) $ pip install -r requirements.txt
(env) $ pip install -e .
```

Deactivate your virtual environment with the `deactivate` command. As long as the environment is not removed, you may start sessions simply with the command `source env/bin/activate`.

**Note**: The `requirements.txt` file contains transitive dependencies in addition to direct dependencies. To reconstruct the requirements from scratch, use the following commands to install the direct dependencies used for development, packaging, and releasing.

```
(env) $ pip install pytest-cov requests nox sphinx sphinx-rtd-theme twine wheel
```

**Note**: If you wish to update the requirements with new or updated packages, run the following.

```sh
(env) $ pip freeze --exclude-editable > requirements.txt
```

#### Testing

The tests require the ProKnow API service to be started with the `PATIENTS_MIN_PAGE_SIZE` environment variable set to `1`. To do this, at the top level of the the ProKnow directory, run

```sh
$ PATIENTS_MIN_PAGE_SIZE=1 npm run start
```

Before you start testing, you'll need access to a ProKnow DS organization where you can generate an [API token](https://support.proknow.com/hc/en-us/articles/360019798893-Configuring-Your-Profile#managing-api-keys) for your project. Once you have your API token create a file called `pktestconfig.py` in the test directory with the following contents:

```
#!/usr/bin/env python
base_url = "https://example.proknow.com"
credentials_id = "{{ id from credentials.json }}"
credentials_secret = "{{ secret from credentials.json }}"
```

Make sure to put your actual base_url and the id and secret from your `credentials.json` file in place of the placeholders above. Note that for testing against a local ProKnow instance, the `base_url` should be set to `http://localhost:3005` and the environment must be configured to use Auth0 as the identity provider (and not Keycloak or OIDC).

Next, run the tests with the `nox` command from within your virtual environment. This command runs the tests against all of the supported Python versions. You may need to install these versions on the host.

```sh
$ nox
```

To run a specific test using python 3, use the following form:

```sh
$ pytest tests/{{file name}}::{{test name}}
```

To run tests with the HTML coverage report, use the following:

```sh
$ pytest --cov=proknow --cov-branch --cov-report html tests
```

#### Building the Documentation

With the virtual environment, you can run `make clean && make html` to build the documentation.

```sh
$ cd docs/
$ make clean && make html
```

## Packaging & Release

First, make sure the version has been updated in setup.py. Then run the following within the virtual environment.

```sh
$ rm -rf dist build */*.egg-info *.egg-info
$ python3 setup.py bdist_wheel --universal
$ python3 -m twine upload dist/*
```
