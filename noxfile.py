import nox

@nox.session(python=['2.7', '3.7'])
def tests(session):
    # Install py.test
    session.install('pytest')
    # Install the current package in editable mode.
    session.install('-e', '.')
    # Run py.test. This uses the py.test executable in the virtualenv.
    session.run('pytest', 'tests', '--cov=proknow', '--cov-branch', '--cov-report', 'term')
