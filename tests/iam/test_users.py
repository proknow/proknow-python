import pytest
import re
import six

from proknow import Exceptions

def test_create(app, user_generator):
    pk = app.pk

    # Verify returned UserItem
    params, user = user_generator()
    assert user.name == params["name"]
    assert user.email == params["email"]
    assert user.active is True
    assert user.role_id == params["role_id"]

    # Assert item can be found in query
    for user in pk.users.query():
        if user.name == params["name"]:
            user_match = user
            break
    else:
        user_match = None
    assert user_match is not None
    user = user_match.get()
    assert isinstance(user.data["id"], six.string_types)
    assert user.name == params["name"]
    assert user.email == params["email"]
    assert user.active is True
    assert user.role_id == params["role_id"]

    # Verify user can be created with password
    params, user = user_generator(password="2pBUYbneE^egW^qX*34v")
    assert user.name == params["name"]
    assert user.email == params["email"]
    assert user.active is True
    assert user.role_id == params["role_id"]

def test_create_failure(app, user_generator):
    pk = app.pk

    params, _ = user_generator()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.users.create(**params)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'User already exists with email "' + params["email"] + '"'

def test_delete(app, user_generator):
    pk = app.pk

    params, user = user_generator(do_not_mark=True)

    # Verify user was deleted successfully
    user.delete()
    for user in pk.users.query():
        if user.email == params["email"]:
            match = user
            break
    else:
        match = None
    assert match is None

def test_delete_failure(app, user_generator):
    pk = app.pk

    params, user = user_generator(do_not_mark=True)

    user.delete()
    # Assert error is raised when attempting to delete user that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        user.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'User "' + user.id + '" not found'

def test_find(app, user_generator):
    pk = app.pk

    params, user = user_generator(name="Find Me")
    expr = re.compile(r"ind")

    # Find with no args
    found = pk.users.find()
    assert found is None

    # Find using predicate
    found = pk.users.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.email == params["email"]
    assert found.name == params["name"]

    # Find using props
    found = pk.users.find(id=user.id, name="Find Me")
    assert found is not None
    assert found.email == params["email"]
    assert found.name == params["name"]

    # Find using both
    found = pk.users.find(lambda ws: expr.search(ws.data["name"]) is not None, id=user.id, name="Find Me")
    assert found is not None
    assert found.email == params["email"]
    assert found.name == params["name"]

    # Find failure
    found = pk.users.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.users.find(id=user.id, name="Find me")
    assert found is None

def test_query(app, user_generator):
    pk = app.pk

    params1, user1 = user_generator()
    params2, user2 = user_generator()

    # Verify test 1
    for user in pk.users.query():
        if user.email == params1["email"]:
            match = user
            break
    else:
        match = None
    assert match is not None
    assert match.id == user1.id
    assert match.email == params1["email"]
    assert match.name == params1["name"]

    # Verify test 2
    for user in pk.users.query():
        if user.email == params2["email"]:
            match = user
            break
    else:
        match = None
    assert match is not None
    assert match.id == user2.id
    assert match.email == params2["email"]
    assert match.name == params2["name"]

def test_update(app, user_generator):
    pk = app.pk
    resource_prefix = app.resource_prefix

    params, user = user_generator()

    # Verify user was updated successfully
    updated_email = resource_prefix + "example+updated@proknow.com"
    user.email = updated_email
    user.name = "Updated User Name"
    user.active = False
    user.save()
    for user in pk.users.query():
        if user.email == updated_email:
            user_match = user
            break
    else:
        user_match = None
    assert user_match is not None
    user = user_match.get()
    assert isinstance(user.data["id"], six.string_types)
    assert user.email == updated_email
    assert user.name == "Updated User Name"
    assert user.active == False

def test_update_failure(app, user_generator):
    pk = app.pk

    params, user = user_generator()
    user.delete()

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        user.email = "example+duplicateme2@proknow.com"
        user.save()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'User "' + user.id + '" not found'
