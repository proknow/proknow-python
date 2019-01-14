__all__ = [
    'Users'
]

import six


class Users(object):
    """

    This class should be used to interact with the users in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Users class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def create(self, email, name, role_id, password=None):
        """Creates a new user.

        Parameters:
            email (str): The email of the user.
            name (str): The name of the user.
            role_id (str): The id of the role for the user.
            password (str, optional): The password of the user.

        Returns:
            :class:`proknow.Users.UserItem`: A representation of the created item.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(email, str), "`email` is required as a string."
        assert isinstance(name, str), "`name` is required as a string."
        assert isinstance(role_id, str), "`role_id` is required as a string."

        body = {
            "email": email,
            "name": name,
            "role_id": role_id,
        }
        if password is not None:
            assert isinstance(password, str), "`password` is required as a string."
            body["password"] = password

        _, user = self._requestor.post('/users', body=body)
        return UserItem(self, user)

    def delete(self, identifier):
        """Deletes a user.

        Parameters:
            identifier (str): The id of the user to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(identifier, six.string_types), "`identifier` is required as a string."
        self._requestor.delete('/users/' + identifier)

    def find(self, **kwargs):
        """Finds a user by id, email, or name.

        Parameters:
            **kwargs: A dictionary of keyword arguments that may include `identifier`, `email`, and
                `name`. These arguments are considered---in that order---to find matching roles.

        Returns:
            :class:`proknow.Users.UserItem`: A representation of the matching user.
        """
        users = self.query()
        if "identifier" in kwargs:
            for user in users:
                if user._id == kwargs["identifier"]:
                    return user
        if "email" in kwargs:
            for user in users:
                if user._data["email"] == kwargs["email"]:
                    return user
        elif "name" in kwargs:
            for user in users:
                if user._data["name"] == kwargs["name"]:
                    return user
        return None

    def get(self, identifier):
        """Gets a user.

        Parameters:
            identifier (str): The id of the user to get.

        Returns:
            :class:`proknow.Users.UserItem`: an object representing a user in the organization
        """
        assert isinstance(identifier, six.string_types), "`identifier` is required as a string."
        _, user = self._requestor.get('/users/' + identifier)
        return UserItem(self, user)

    def query(self):
        """Queries for users.

        Returns:
            list: A list of :class:`proknow.Users.UserSummary` objects, each representing a
            summarized user in the organization.
        """
        _, users = self._requestor.get('/users')
        return [UserSummary(self, user) for user in users]

class UserSummary(object):
    """

    This class represents a summary view of a user. It's instantiated by the
    :meth:`proknow.Users.Users.query` method to represent each of the users returned in a query
    result.

    Attributes:
        id (str): The id of the user (readonly).
        email (str): The email of the user (readonly).
        name (str): The name of the user (readonly).
        data (dict): The summary representation of the user as returned from the API (readonly).

    """

    def __init__(self, users, user):
        """Initializes the UserSummary class.

        Parameters:
            users (proknow.Users.Users): The User instance that is instantiating the object.
            user (dict): A dictionary of user attributes.
        """
        self._users = users
        self._requestor = self._users._requestor
        self._id = user["id"]
        self._email = user["email"]
        self._name = user["name"]
        self._data = user

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the user.

        Returns:
            :class:`proknow.Users.UserItem`: an object representing a user in the organization
        """
        return self._users.get(self._id)

class UserItem(object):
    """

    This class represents a user. It's instantiated by the :class:`proknow.Users.Users` class as a
    complete representation of a user.

    Attributes:
        id (str): The id of the user (readonly).
        data (dict): The complete representation of the user as returned from the API (readonly).
        name (str): The name of the user.
        email (str): The email of the user.
        active (bool): Indicates whether the user is active.
        role_id (str): The id of the role for the user.

    """

    def __init__(self, users, user):
        """Initializes the UserItem class.

        Parameters:
            users (proknow.Users.Users): The User instance that is instantiating the object.
            user (dict): A dictionary of user attributes.
        """
        self._users = users
        self._requestor = self._users._requestor
        self._id = user["id"]
        self._data = user
        self.name = user["name"]
        self.email = user["email"]
        self.active = user["active"]
        self.role_id = user["role"]["id"]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the user."""
        self._users.delete(self._id)

    def save(self):
        """Saves the changes made to a user.

        Example:
            The following example illustrates how to find a user by its email, set it to inactive,
            and save it::

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                jsmith = pk.users.find(email='jsmith@example.com')
                jsmith.active = False
                jsmith.save()
        """
        body = {
            "email": self.email,
            "name": self.name,
            "role_id": self.role_id,
            "active": self.active
        }
        _, user = self._requestor.put('/users/' + self._id, body=body)
        self._data = user
        self.name = user["name"]
        self.email = user["email"]
        self.active = user["active"]
        self.role_id = user["role"]["id"]
