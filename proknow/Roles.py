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

    def create(self, name, permissions):
        """Creates a new role.

        Parameters:
            name (str): The name of the role.
            permissions (dict): A dictionary of permissions.

        Returns:
            :class:`proknow.Roles.RoleItem`: A representation of the created item.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new role called "Researchers" with full permissions on the
            "Research" workspace::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.roles.create("Researchers", {
                    "create_api_keys": False,
                    "manage_access": False,
                    "manage_custom_metrics": False,
                    "manage_template_metric_sets": False,
                    "manage_renaming_rules": False,
                    "manage_template_checklists": False,
                    "organization_read": False,
                    "organization_view_phi": False,
                    "organization_download_dicom": False,
                    "organization_write_collections": False,
                    "organization_write_patients": False,
                    "organization_contour_patients": False,
                    "organization_delete_collections": False,
                    "organization_delete_patients": False,
                    "workspaces": [{
                        "id": pk.workspaces.find(name="Research").id,
                        "read": True,
                        "view_phi": True,
                        "download_dicom": True,
                        "write_collections": True,
                        "write_patients": True,
                        "contour_patients": True,
                        "delete_collections": True,
                        "delete_patients": True,
                    }],
                })
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(permissions, dict), "`permissions` is required as a dict."

        body = {
            "name": name,
            "create_api_keys": permissions["create_api_keys"],
            "manage_access": permissions["manage_access"],
            "manage_custom_metrics": permissions["manage_custom_metrics"],
            "manage_template_metric_sets": permissions["manage_template_metric_sets"],
            "manage_renaming_rules": permissions["manage_renaming_rules"],
            "manage_template_checklists": permissions["manage_template_checklists"],
            "organization_read": permissions["organization_read"],
            "organization_view_phi": permissions["organization_view_phi"],
            "organization_download_dicom": permissions["organization_download_dicom"],
            "organization_write_collections": permissions["organization_write_collections"],
            "organization_write_patients": permissions["organization_write_patients"],
            "organization_contour_patients": permissions["organization_contour_patients"],
            "organization_delete_collections": permissions["organization_delete_collections"],
            "organization_delete_patients": permissions["organization_delete_patients"],
            "workspaces": permissions["workspaces"],
        }

        _, role = self._requestor.post('/roles', body=body)
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
            :class:`proknow.Roles.RoleItem`: an object representing a role in the organization

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the role id, you can get the role directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                researchers = pk.roles.get('5c463a6c040068100c7f665acad17ac4')
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
        self._data = role

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the role.

        Returns:
            :class:`proknow.Roles.RoleItem`: an object representing a role in the organization

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
        data (dict): The complete representation of the role as returned from the API (readonly).
        name (str): The name of the role.
        permissions (dict): The dictionary of role permissions.

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
        self.permissions = {
            "create_api_keys": role["create_api_keys"],
            "manage_access": role["manage_access"],
            "manage_custom_metrics": role["manage_custom_metrics"],
            "manage_template_metric_sets": role["manage_template_metric_sets"],
            "manage_renaming_rules": role["manage_renaming_rules"],
            "manage_template_checklists": role["manage_template_checklists"],
            "organization_read": role["organization_read"],
            "organization_view_phi": role["organization_view_phi"],
            "organization_download_dicom": role["organization_download_dicom"],
            "organization_write_collections": role["organization_write_collections"],
            "organization_write_patients": role["organization_write_patients"],
            "organization_contour_patients": role["organization_contour_patients"],
            "organization_delete_collections": role["organization_delete_collections"],
            "organization_delete_patients": role["organization_delete_patients"],
            "workspaces": role["workspaces"],
        }

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
                researchers = pk.roles.find(name='researchers').get()
                researchers.delete()
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
                researchers = pk.roles.find(name='researchers').get()
                researchers.permissions["organization_read"] = True
                researchers.save()
        """
        body = {
            "name": self.name,
            "create_api_keys": self.permissions["create_api_keys"],
            "manage_access": self.permissions["manage_access"],
            "manage_custom_metrics": self.permissions["manage_custom_metrics"],
            "manage_template_metric_sets": self.permissions["manage_template_metric_sets"],
            "manage_renaming_rules": self.permissions["manage_renaming_rules"],
            "manage_template_checklists": self.permissions["manage_template_checklists"],
            "organization_read": self.permissions["organization_read"],
            "organization_view_phi": self.permissions["organization_view_phi"],
            "organization_download_dicom": self.permissions["organization_download_dicom"],
            "organization_write_collections": self.permissions["organization_write_collections"],
            "organization_write_patients": self.permissions["organization_write_patients"],
            "organization_contour_patients": self.permissions["organization_contour_patients"],
            "organization_delete_collections": self.permissions["organization_delete_collections"],
            "organization_delete_patients": self.permissions["organization_delete_patients"],
            "workspaces": self.permissions["workspaces"],
        }
        _, role = self._requestor.put('/roles/' + self._id, body=body)
        self._data = role
        self.name = role["name"]
        self.permissions = {
            "create_api_keys": role["create_api_keys"],
            "manage_access": role["manage_access"],
            "manage_custom_metrics": role["manage_custom_metrics"],
            "manage_template_metric_sets": role["manage_template_metric_sets"],
            "manage_renaming_rules": role["manage_renaming_rules"],
            "manage_template_checklists": role["manage_template_checklists"],
            "organization_read": role["organization_read"],
            "organization_view_phi": role["organization_view_phi"],
            "organization_download_dicom": role["organization_download_dicom"],
            "organization_write_collections": role["organization_write_collections"],
            "organization_write_patients": role["organization_write_patients"],
            "organization_contour_patients": role["organization_contour_patients"],
            "organization_delete_collections": role["organization_delete_collections"],
            "organization_delete_patients": role["organization_delete_patients"],
            "workspaces": role["workspaces"],
        }
