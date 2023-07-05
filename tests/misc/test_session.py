import pytest

def test_http_error(app):
    pk = app.pk

    session = pk.session.get()
    assert isinstance(session, dict)
    assert isinstance(session["id"], str)
    assert isinstance(session["email"], str)
    assert isinstance(session["name"], str)
    assert session["active"] == True
    assert isinstance(session["federated"], bool)
    assert isinstance(session["created_at"], str)
