import six

from .Patients import CollectionPatients
from .Scorecards import CollectionScorecards


class Collections(object):
    """

    This class should be used to interact with the collections in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.Collections.Collections` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Collections class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def create(self, name, description, type, workspaces):
        """Creates a new collection.

        Parameters:
            name (str): The name of the collection.
            description (str): The description of the collection.
            type (str): The type of the collection (either "workspace" or "organization").
            workspaces (list): A list of workspace ids. For workspace collections, there must be
                exactly one workspace id in this list.

        Returns:
            :class:`proknow.Collections.CollectionItem`: A representation of the created collection.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new organization collection called "My Collection"::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.collections.create("My Collection", "", "organization", [])

            This example creates a new workspace collection called "My Workspace Collection"::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.collections.create("My Workspace Collection", "", "workspace", [
                    pk.workspaces.find(name="Clinical").id
                ])
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(description, six.string_types), "`description` is required as a string."
        assert isinstance(type, six.string_types), "`type` is required as a string."
        assert isinstance(workspaces, list), "`workspaces` is required as a list."

        body = {
            "name": name,
            "description": description,
            "type": type,
            "workspaces": workspaces,
        }

        _, collection = self._requestor.post('/collections', json=body)
        return CollectionItem(self, collection)

    def delete(self, collection_id):
        """Deletes a collection.

        Parameters:
            collection_id (str): The id of the collection to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the collection id, you can delete the collection directly using this
            method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.collections.delete('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(collection_id, six.string_types), "`collection_id` is required as a string."
        self._requestor.delete('/collections/' + collection_id)

    def find(self, workspace=None, predicate=None, **props):
        """Finds the first collection that matches the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Parameters:
            workspace (str, optional): An id or name of the workspace in which to query for
                workspace representations of collections. If a workspace is not provided, only
                organization collections will be considered.
            predicate (func): A function that is passed a collection as input and which should
                return a bool indicating whether the collection is a match.
            **props: A dictionary of keyword arguments that may include any collection attribute.
                These arguments are considered in turn to find matching collections.

        Returns:
            :class:`proknow.Collections.CollectionItem`: A representation of the matching
            collection.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        if predicate is None and len(props) == 0:
            return None

        collections = self.query(workspace)
        for collection in collections:
            match = True
            if predicate is not None and not predicate(collection):
                match = False
            for key in props:
                if collection._data[key] != props[key]:
                    match = False
            if match:
                return collection

        return None

    def get(self, collection_id):
        """Gets a collection.

        Parameters:
            collection_id (str): The id of the collection to get.

        Returns:
            :class:`proknow.Collections.CollectionItem`: An object representing a collection in the
            organization

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the collection id, you can get the collection directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(collection_id, six.string_types), "`collection_id` is required as a string."
        _, collection = self._requestor.get('/collections/' + collection_id)
        return CollectionItem(self, collection)

    def query(self, workspace=None):
        """Queries for collections.

        Parameters:
            workspace (str, optional): An id or name of the workspace in which to query for
                workspace representations of collections. If a workspace is not provided, only
                organization collections will be returned.

        Returns:
            list: A list of :class:`proknow.Collections.CollectionSummary` objects, each
            representing a summarized collection in the organization.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the collections and prints the name of each collection::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                for collection in pk.collections.query():
                    print(collection.name)
        """
        query = {}
        if workspace is not None:
            assert isinstance(workspace, six.string_types), "`workspace` is required as a string."
            query["workspace"] = self._proknow.workspaces.resolve(workspace).id

        _, collections = self._requestor.get('/collections', params=query)
        return [CollectionSummary(self, collection) for collection in collections]

class CollectionSummary(object):
    """

    This class represents a summary view of a collection. It's instantiated by the
    :meth:`proknow.Collections.Collections.query` method to represent each of the collections
    returned in a query result.

    Attributes:
        id (str): The id of the collection (readonly).
        name (str): The name of the collection (readonly).
        description (str): The description of the collection (readonly).
        data (dict): The summary representation of the collection as returned from the API
            (readonly).

    """

    def __init__(self, collections, collection):
        """Initializes the CollectionSummary class.

        Parameters:
            collections (proknow.Collections.Collections): The Collections instance that is
                instantiating the object.
            collection (dict): A dictionary of collection attributes.
        """
        self._collections = collections
        self._requestor = self._collections._requestor
        self._id = collection["id"]
        self._name = collection["name"]
        self._description = collection["description"]
        self._data = collection

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
        """Gets the complete representation of the collection.

        Returns:
            :class:`proknow.Collections.CollectionItem`: An object representing a collection in the
            organization

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of CollectionSummary objects into a list
            of CollectionItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collections = [collection.get() for collection in pk.collections.query()]
        """
        return self._collections.get(self._id)

class CollectionItem(object):
    """

    This class represents a collection. It's instantiated by the
    :class:`proknow.Collections.Collections` class as a complete representation of a collection.

    Attributes:
        id (str): The id of the collection (readonly).
        data (dict): The complete representation of the collection as returned from the API
            (readonly).
        name (str): The name of the collection.
        description (str): The description of the collection.
        patients (proknow.Collections.CollectionPatients): An object for interacting with the
            patients within a collection.
        scorecards (proknow.Collections.CollectionScorecards): An object for interacting with the
            scorecards belonging to the collection.

    """

    def __init__(self, collections, collection):
        """Initializes the CollectionItem class.

        Parameters:
            collections (proknow.Collections.Collections): The Collection instance that is
                instantiating the object.
            collection (dict): A dictionary of collection attributes.
        """
        self._collections = collections
        self._requestor = self._collections._requestor
        self._id = collection["id"]
        self._data = collection
        self.name = collection["name"]
        self.description = collection["description"]
        self.patients = CollectionPatients(self._collections, self)
        self.scorecards = CollectionScorecards(self._collections, self)

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the collection.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a collection by its name and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                collection.delete()
        """
        self._collections.delete(self._id)

    def save(self):
        """Saves the changes made to a collection.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a collection by its name, edit the
            description, and save it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                collection.description = "This is my collection."
                collection.save()
        """
        body = {
            "name": self.name,
            "description": self.description,
        }
        _, collection = self._requestor.put('/collections/' + self._id, json=body)
        self._data = collection
        self.name = collection["name"]
        self.description = collection["description"]
