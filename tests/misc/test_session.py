import pytest
import six

def test_http_error(app):
    pk = app.pk

    session = pk.session.get()
    assert isinstance(session, dict)
    assert isinstance(session["id"], six.string_types)
    assert isinstance(session["email"], six.string_types)
    assert isinstance(session["name"], six.string_types)
    assert session["active"] == True
    assert isinstance(session["federated"], bool)
    assert isinstance(session["created_at"], six.string_types)
    assert isinstance(session["role"], dict)
