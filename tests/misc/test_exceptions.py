import pytest

from proknow import Exceptions

def test_http_error():
    err = Exceptions.HttpError(200, 'example response body')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "HttpError(200, 'example response body')"
    assert str(err) == "HttpError(200, 'example response body')"

def test_workspace_lookup_error():
    err = Exceptions.WorkspaceLookupError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "WorkspaceLookupError('custom message')"
    assert str(err) == "WorkspaceLookupError('custom message')"

def test_custom_metric_lookup_error():
    err = Exceptions.CustomMetricLookupError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "CustomMetricLookupError('custom message')"
    assert str(err) == "CustomMetricLookupError('custom message')"

def test_invalid_operation_error():
    err = Exceptions.InvalidOperationError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "InvalidOperationError('custom message')"
    assert str(err) == "InvalidOperationError('custom message')"

def test_invalid_path_error():
    err = Exceptions.InvalidPathError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "InvalidPathError('custom message')"
    assert str(err) == "InvalidPathError('custom message')"

def test_scorecard_template_lookup_error():
    err = Exceptions.ScorecardTemplateLookupError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "ScorecardTemplateLookupError('custom message')"
    assert str(err) == "ScorecardTemplateLookupError('custom message')"

def test_timeout_exceeded_error():
    err = Exceptions.TimeoutExceededError('custom message')
    assert isinstance(err, Exceptions.ProKnowError)
    assert repr(err) == "TimeoutExceededError('custom message')"
    assert str(err) == "TimeoutExceededError('custom message')"
