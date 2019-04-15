import pytest
import re
import six

from proknow import Exceptions

def test_create_users(app):
    pk = app.pk

    # Verify returned UserItem
    role_id = pk.roles.find(name="Admin").id
    user = pk.users.create("example+create_test@proknow.com", "Create Test", role_id)
    app.marked_users.append(user) # mark for removal
    assert user.name == "Create Test"
    assert user.email == "example+create_test@proknow.com"
    assert user.active is True
    assert user.role_id == role_id

    # Assert item can be found in query
    for user in pk.users.query():
        if user.name == "Create Test":
            user_match = user
            break
    else:
        user_match = None
    assert user_match is not None
    user = user_match.get()
    assert isinstance(user.data["id"], six.string_types)
    assert user.name == "Create Test"
    assert user.email == "example+create_test@proknow.com"
    assert user.active is True
    assert user.role_id == role_id

    # Verify user can be created with password
    user = pk.users.create("example+create_test2@proknow.com", "Create Test 2", role_id, "2pBUYbneE^egW^qX*34v")
    app.marked_users.append(user) # mark for removal
    assert user.name == "Create Test 2"
    assert user.email == "example+create_test2@proknow.com"
    assert user.active is True
    assert user.role_id == role_id

def test_create_users_failure(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user_factory(("example+duplicateme@proknow.com", "Duplicate Me", role_id))

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        pk.users.create("example+duplicateme@proknow.com", "Duplicate Me", role_id)
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'User already exists with email "example+duplicateme@proknow.com"'

def test_delete_users(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user = user_factory(("example+deleteme@proknow.com", "Delete Me", role_id), do_not_mark=True)[0]

    # Verify user was deleted successfully
    user.delete()
    for user in pk.users.query():
        if user.email == "example+deleteme@proknow.com":
            match = user
            break
    else:
        match = None
    assert match is None

def test_delete_users_failure(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user = user_factory(("example+deleteme2@proknow.com", "Delete Me 2", role_id), do_not_mark=True)[0]

    user.delete()

    # Assert error is raised when attempting to delete user that does not exist
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        user.delete()
    assert err_wrapper.value.status_code == 404
    assert err_wrapper.value.body == 'User "' + user.id + '" not found.'

def test_find_users(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user = user_factory(("example+findme@proknow.com", "Find Me", role_id))[0]
    expr = re.compile(r"ind")

    # Find with no args
    found = pk.users.find()
    assert found is None

    # Find using predicate
    found = pk.users.find(lambda ws: expr.search(ws.data["name"]) is not None)
    assert found is not None
    assert found.email == "example+findme@proknow.com"
    assert found.name == "Find Me"

    # Find using props
    found = pk.users.find(id=user.id, name="Find Me")
    assert found is not None
    assert found.email == "example+findme@proknow.com"
    assert found.name == "Find Me"

    # Find using both
    found = pk.users.find(lambda ws: expr.search(ws.data["name"]) is not None, id=user.id, name="Find Me")
    assert found is not None
    assert found.email == "example+findme@proknow.com"
    assert found.name == "Find Me"

    # Find failure
    found = pk.users.find(lambda ws: expr.search(ws.data["id"]) is not None)
    assert found is None
    found = pk.users.find(id=user.id, name="Find me")
    assert found is None

def test_query_users(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    result = user_factory([
        ("example+test_1@proknow.com", "Test User 1", role_id),
        ("example+test_2@proknow.com", "Test User 2", role_id),
    ])

    # Verify test 1
    for user in pk.users.query():
        if user.email == "example+test_1@proknow.com":
            match = user
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[0].id
    assert match.email == "example+test_1@proknow.com"
    assert match.name == "Test User 1"

    # Verify test 2
    for user in pk.users.query():
        if user.email == "example+test_2@proknow.com":
            match = user
            break
    else:
        match = None
    assert match is not None
    assert match.id == result[1].id
    assert match.email == "example+test_2@proknow.com"
    assert match.name == "Test User 2"

def test_update_users(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user = user_factory(("example+updateme@proknow.com", "Update Me", role_id))[0]

    # Verify user was updated successfully
    user.email = "example+updated@proknow.com"
    user.name = "Updated User Name"
    user.active = False
    user.save()
    for user in pk.users.query():
        if user.email == "example+updated@proknow.com":
            user_match = user
            break
    else:
        user_match = None
    assert user_match is not None
    user = user_match.get()
    assert isinstance(user.data["id"], six.string_types)
    assert user.email == "example+updated@proknow.com"
    assert user.name == "Updated User Name"
    assert user.active == False

def test_update_users_failure(app, user_factory):
    pk = app.pk

    role_id = pk.roles.find(name="Admin").id
    user = user_factory([
        ("example+updateme_failure@proknow.com", "Update Me Failure", role_id),
        ("example+duplicateme2@proknow.com", "Duplicate Me 2", role_id),
    ])[0]

    # Assert error is raised for duplicate workspace
    with pytest.raises(Exceptions.HttpError) as err_wrapper:
        user.email = "example+duplicateme2@proknow.com"
        user.save()
    assert err_wrapper.value.status_code == 409
    assert err_wrapper.value.body == 'User already exists with email "example+duplicateme2@proknow.com"'
