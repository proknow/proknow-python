import nox

@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def tests(session):
    # Install py.test
    session.install('pytest', 'pytest-cov')
    # Install the current package in editable mode.
    session.install('-e', '.')
    # Run py.test. This uses the py.test executable in the virtualenv.
    session.run('pytest', '--cov=proknow', '--cov-append', '--cov-branch', '--cov-report', 'html', 'tests')
