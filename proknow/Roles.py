__all__ = [
    'Roles'
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
        """
        assert isinstance(name, str), "`name` is required as a string."
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

    def delete(self, identifier):
        """Deletes a role.

        Parameters:
            identifier (str): The id of the role to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(identifier, six.string_types), "`identifier` is required as a string."
        self._requestor.delete('/roles/' + identifier)

    def find(self, **kwargs):
        """Finds a role by id or name.

        Parameters:
            **kwargs: A dictionary of keyword arguments that may include `identifier` and `name`.
                These arguments are considered---in that order---to find matching roles.

        Returns:
            :class:`proknow.Roles.RoleItem`: A representation of the matching role.
        """
        roles = self.query()
        if "identifier" in kwargs:
            for role in roles:
                if role._id == kwargs["identifier"]:
                    return role
        elif "name" in kwargs:
            for role in roles:
                if role._data["name"] == kwargs["name"]:
                    return role
        return None

    def get(self, identifier):
        """Gets a role.

        Parameters:
            identifier (str): The id of the role to get.

        Returns:
            :class:`proknow.Roles.RoleItem`: an object representing a role in the organization
        """
        assert isinstance(identifier, six.string_types), "`identifier` is required as a string."
        _, role = self._requestor.get('/roles/' + identifier)
        return RoleItem(self, role)

    def query(self):
        """Queries for roles.

        Returns:
            list: A list of :class:`proknow.Roles.RoleSummary` objects, each representing a
            summarized role in the organization.
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
            roles (proknow.Roles.Roles): The Role instance that is instantiating the object.
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
        """Deletes the role."""
        self._roles.delete(self._id)

    def save(self):
        """Saves the changes made to a role.

        Example:
            The following example illustrates how to find a role by its slug, modify a permission,
            and save it::

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                researchers = pk.roles.find(name='researchers')
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
