# ProKnow DS - Python SDK

The ProKnow DS - Python SDK library provides convenient access to the ProKnow API from applications written in the Python language. It includes a pre-defined set of classes for API resources that initialize themselves dynamically from API responses.

## Development

### Mac OSX

1. Install the latest version of python. This will be installed alongside the version that your operating system provides.
2. Run the following to install/upgrade `pip`, `setuptools` and `wheel`.
```
python3 -m pip install --upgrade pip setuptools wheel
```
3. Create a virtual environment. Note that this will create the directories `bin/`, `include/`, and `/lib` and the file pyvenv.cfg. These files should be ignored in your distribution
```
python3 -m venv ./
```
4. Activate the virtual environment. You'll need to do this again each time you open the project in a new terminal window.
```
source ./bin/activate
```

Once the virtual environment has been activated, you can use `python` and `pip` to refer to `python3` and `pip3`. For example, the following command can be used to install the current directory as a development package allowing you to continue to develop the package without reinstalling it after each change is made.

```
pip install -e ./
```

To make the documentation, you'll need to install sphinx with the following command (after initializing your development environment with `source ./bin/activate`).

```
pip install sphinx
```

Then run `make` in the `docs/` directory to build the documentation.
