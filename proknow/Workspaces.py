__all__ = [
    'Workspaces'
]

import six


class Workspaces(object):
    """

    This class should be used to interact with the workspaces in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Workspaces class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor
        self._cache = None

    def create(self, slug, name, protected=True):
        """Creates a new workspace.

        Parameters:
            slug (str): The workspace slug.
            name (str): The workspace name.
            protected (bool, optional): Indicates whether the workspace should be protected from
                accidental deletion.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the created workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(slug, six.string_types), "`slug` is required as a string."
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(protected, bool), "`protected` is required as a bool."

        _, workspace = self._requestor.post('/workspaces', body={'slug': slug, 'name': name, 'protected': protected})
        self._cache = None
        return WorkspaceItem(self, workspace)

    def delete(self, identifier):
        """Deletes a workspace.

        Parameters:
            identifier (str): The id of the workspace to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(identifier, six.string_types), "`identifier` is required as a string."
        self._requestor.delete('/workspaces/' + identifier)
        self._cache = None

    def find(self, **kwargs):
        """Finds a workspace by id, slug, or name.

        Note:
            This method utilizes a cache of workspaces. Once it has a cache of workspaces, it will
            use that cache until the :meth:`proknow.Workspaces.Workspaces.query` method is called
            to refresh the cache. If you wish to make your code resilient to workspaces changes
            (i.e., new workspaces, renamed workspaces, deleted workspaces, etc.) while your script
            is running, you should call the :meth:`proknow.Workspaces.Workspaces.query` method
            before this method. In most use cases, this is not necessary.

        Parameters:
            **kwargs: A dictionary of keyword arguments that may include `identifier`, `slug`, and
                `name`. These arguments are considered---in that order---to find matching
                workspaces.

        Returns:
            :class:`proknow.Workspaces.WorkspaceItem`: A representation of the matching workspace.
        """
        if self._cache is None:
            self.query()
        if "identifier" in kwargs:
            for workspace in self._cache:
                if workspace._id == kwargs["identifier"]:
                    return workspace
        elif "slug" in kwargs:
            for workspace in self._cache:
                if workspace.data["slug"] == kwargs["slug"]:
                    return workspace
        elif "name" in kwargs:
            for workspace in self._cache:
                if workspace.data["name"] == kwargs["name"]:
                    return workspace
        return None

    def query(self):
        """Queries for workspaces.

        Note:
            This method refreshes the workspaces cache.

        Returns:
            list: A list of :class:`proknow.Workspaces.WorkspaceItem` objects, each representing a
            workspace in the organization.
        """
        _, workspaces = self._requestor.get('/workspaces')
        self._cache = [WorkspaceItem(self, workspace) for workspace in workspaces]
        return self._cache

class WorkspaceItem(object):
    """

    This class represents a workspace. It's instantiated by the
    :class:`proknow.Workspaces.Workspaces` class to represent each of the workspaces in a query
    result and a created workspace.

    Attributes:
        id (str): The id of the workspace (readonly).
        data (dict): The complete representation of the workspace as returned from the API
            (readonly).
        slug (str): A string used in the URL that uniquely identifies the workspace.
        name (str): The name of the workspace.
        protected (bool): Indicates whether the workspace should be protected from accidental
            deletion.

    """

    def __init__(self, workspaces, workspace):
        """Initializes the WorkspaceItem class.

        Parameters:
            workspaces (proknow.Workspaces.Workspaces): The Workspaces instance that is instantiating
                the object.
            workspace (dict): A dictionary of workspace attributes.
        """
        self._workspaces = workspaces
        self._requestor = self._workspaces._requestor
        self._id = workspace["id"]
        self._data = workspace
        self.slug = workspace["slug"]
        self.name = workspace["name"]
        self.protected = workspace["protected"]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the workspace."""
        self._workspaces.delete(self._id)

    def save(self):
        """Saves the changes made to a workspace.

        Example:
            The following example illustrates how to find a workspace by its slug, modify the name,
            and save it::

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                clinical = pk.workspaces.find(slug='clinical')
                clinical.name = "Clinical Patients"
                clinical.save()
        """
        _, workspace = self._requestor.put('/workspaces/' + self._id, body={'slug': self.slug, 'name': self.name, 'protected': self.protected})
        self._data = workspace
        self.slug = workspace["slug"]
        self.name = workspace["name"]
        self.protected = workspace["protected"]
