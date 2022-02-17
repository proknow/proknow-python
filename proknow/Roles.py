__all__ = [
    'Roles',
]

import six


class Roles(object):
    """

    This class should be used to interact with the roles in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Roles class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def create(self, name, description, permissions):
        """Creates a new role.

        Parameters:
            name (str): The name of the role.
            description (str): The description of the role.
            permissions (dict): A dictionary of permissions. Note that the permissions dictionary does not have to include all permissions.

        Returns:
            :class:`proknow.Roles.RoleItem`: A representation of the created item.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new role called "Renaming Rule Maintainer"::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.roles.create("Renaming Rule Maintainer", "Role description", {
                    "renaming_rules_search": True,
                    "renaming_rules_update": True,
                    "renaming_rules_execute": True,
                    "structure_set_templates_read": True
                })
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(description, six.string_types), "`description` is required as a string."
        assert isinstance(permissions, dict), "`permissions` is required as a dict."

        body = {}
        body["permissions"] = dict(permissions)
        body["name"] = name
        body["description"] = description

        _, role = self._requestor.post('/roles', json=body)
        return RoleItem(self, role)

    def delete(self, role_id):
        """Deletes a role.

        Parameters:
            role_id (str): The id of the role to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the role id, you can delete the role directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.roles.delete('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(role_id, six.string_types), "`role_id` is required as a string."
        self._requestor.delete('/roles/' + role_id)

    def find(self, predicate=None, **props):
        """Finds the first role that matches the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Parameters:
            predicate (func): A function that is passed a role as input and which should return
                a bool indicating whether the role is a match.
            **props: A dictionary of keyword arguments that may include any role attribute.
                These arguments are considered in turn to find matching roles.

        Returns:
            :class:`proknow.Roles.RoleItem`: A representation of the matching role.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        roles = self.query()
        if predicate is None and len(props) == 0:
            return None

        for role in roles:
            match = True
            if predicate is not None and not predicate(role):
                match = False
            for key in props:
                if role._data[key] != props[key]:
                    match = False
            if match:
                return role

        return None

    def get(self, role_id):
        """Gets a role.

        Parameters:
            role_id (str): The id of the role to get.

        Returns:
            :class:`proknow.Roles.RoleItem`: An object representing a role in the organization

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the role id, you can get the role directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                renaming_rule_maintainer = pk.roles.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(role_id, six.string_types), "`role_id` is required as a string."
        _, role = self._requestor.get('/roles/' + role_id)
        return RoleItem(self, role)

    def query(self):
        """Queries for roles.

        Returns:
            list: A list of :class:`proknow.Roles.RoleSummary` objects, each representing a
            summarized role in the organization.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the roles and prints the name of each role::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                for role in pk.roles.query():
                    print(role.name)
        """
        _, roles = self._requestor.get('/roles')
        return [RoleSummary(self, role) for role in roles]

class RoleSummary(object):
    """

    This class represents a summary view of a role. It's instantiated by the
    :meth:`proknow.Roles.Roles.query` method to represent each of the roles returned in a query
    result.

    Attributes:
        id (str): The id of the role (readonly).
        name (str): The name of the role (readonly).
        description (str): The description of the role (readonly).
        data (dict): The summary representation of the role as returned from the API (readonly).

    """

    def __init__(self, roles, role):
        """Initializes the RoleSummary class.

        Parameters:
            roles (proknow.Roles.Roles): The Roles instance that is instantiating the object.
            role (dict): A dictionary of role attributes.
        """
        self._roles = roles
        self._requestor = self._roles._requestor
        self._id = role["id"]
        self._name = role["name"]
        self._description = role["description"]
        self._data = role

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the role.

        Returns:
            :class:`proknow.Roles.RoleItem`: An object representing a role in the organization

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of RoleSummary objects into a list of
            RoleItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                roles = [role.get() for role in pk.roles.query()]
        """
        return self._roles.get(self._id)

class RoleItem(object):
    """

    This class represents a role. It's instantiated by the :class:`proknow.Roles.Roles` class as a
    complete representation of a role.

    Attributes:
        id (str): The id of the role (readonly).
        name (str): The name of the role.
        description (str): The description of the role.
        permissions (dict): The dictionary of role permissions.
        data (dict): The complete representation of the role as returned from the API (readonly).

    """

    def __init__(self, roles, role):
        """Initializes the RoleItem class.

        Parameters:
            roles (proknow.Roles.Roles): The Role instance that is instantiating the object.
            role (dict): A dictionary of role attributes.
        """
        self._roles = roles
        self._requestor = self._roles._requestor
        self._id = role["id"]
        self._data = role
        self.name = role["name"]
        self.description = role["description"]
        self.system = role["system"]
        self.permissions = dict(role["permissions"])

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the role.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a role by its name and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                renaming_rule_maintainer = pk.roles.find(name='Renaming Rule Maintainer').get()
                renaming_rule_maintainer.delete()
        """
        self._roles.delete(self._id)

    def save(self):
        """Saves the changes made to a role.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a role by its name, modify a permission,
            and save it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                renaming_rule_maintainer = pk.roles.find(name='Renaming Rule Maintainer').get()
                renaming_rule_maintainer.name = "new renaming rule maintainer name"
                renaming_rule_maintainer.permissions["collections_read"] = True
                renaming_rule_maintainer.save()
        """
        body = {}
        body["permissions"] = dict(self.permissions)
        body["name"] = self.name
        body["description"] = self.description
        _, role = self._requestor.patch('/roles/' + self._id, json=body)
        self._data = role
        self.name = role["name"]
        self.description = role["description"]
        self.system = role["system"]
        self.permissions = dict(role["permissions"])
