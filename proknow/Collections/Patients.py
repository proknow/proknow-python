class CollectionPatients(object):
    """

    This class should be used for interacting with the patients for a collection.

    """

    def __init__(self, collections, collection):
        """Initializes the CollectionPatients class.

        Parameters:
            collections (proknow.Collections.Collections): The Collections instance that is
                instantiating the object.
            collection (proknow.Collections.CollectionItem): A instance of a CollectionItem.
        """
        self._collections = collections
        self._collection = collection
        self._proknow = self._collections._proknow
        self._requestor = self._collection._requestor

    def _query(self, query=None):
        res, data = self._requestor.get('/collections/' + self._collection.id + '/patients', params=query)
        if res.headers['proknow-has-more'] == 'true': # pragma: no cover (difficult to test w/o lg num of patients)
            if query is None:
                query = {}
            next_query = dict(query)
            next_query["next"] = res.headers['proknow-next']
            return data + self._query(next_query)
        else:
            return data

    def add(self, workspace, items):
        """Add patients (with optional representative entities) within a workspace to the collection.

        Parameters:
            workspace (str): An id or name of the workspace in which to find the patient(s).
            items (list): A list of dictionary objects containing the key "patient" and, optionally,
                the key "entity." The values of these fields must be ids.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.

        Example:
            The following example shows how to add three patients with dose entities to a
            collection::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name="My Collection").get()
                patients = pk.patients.lookup("Clinical", ["1802-2891", "3812-3239", "5800-2495"])
                items = []
                for summary in patients:
                    patient = summary.get()
                    dose = patient.find_entities(type="dose")[0]
                    items.append({
                        "patient": patient.id,
                        "entity": dose.id
                    })
                collection.patients.add("Clinical", items)
        """
        item = self._proknow.workspaces.resolve(workspace)
        self._requestor.put('/collections/' + self._collection.id + '/workspaces/' + item.id + '/patients', json=items)

    def query(self):
        """Queries for patients belonging to the collection.

        Returns:
            list: A list of :class:`proknow.Collections.CollectionPatientSummary` objects, each
            representing a summarized patient in the collection.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to query for patients in a collection and print each
            patient ID::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name="My Collection").get()
                for patient in collection.patients.query():
                    print(patient.data["patient"]["mrn"])
        """
        if self._collection.data["type"] == 'organization':
            patients = self._query()
        else: # == 'workspace'
            patients = self._query({
                "workspace": self._collection.data["workspaces"][0]
            })
        return [CollectionPatientSummary(self._collections, patient) for patient in patients]

    def remove(self, workspace, items):
        """Remove patients within a workspace from the collection.

        Parameters:
            workspace (str): An id or name of the workspace in which to find the patient(s).
            items (list): A list of dictionary objects containing the key "patient." The value of
                this field must be an id.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.

        Example:
            The following example shows how to remove three patients from a collection::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name="My Collection").get()
                patients = pk.patients.lookup("Clinical", ["1802-2891", "3812-3239", "5800-2495"])
                items = [{ "patient": patient.id } for patient in patients]
                collection.patients.remove("Clinical", items)
        """
        item = self._proknow.workspaces.resolve(workspace)
        self._requestor.delete('/collections/' + self._collection.id + '/workspaces/' + item.id + '/patients', json=items)

class CollectionPatientSummary(object):
    """

    This class represents a summary view of a patient.

    Attributes:
        id (str): The id of the patient (readonly).
        entity_id (str): The id of the entity if specified (readonly).
        data (dict): The summary representation of the collection patient as returned from the API
            (readonly).

    """

    def __init__(self, collections, summary):
        """Initializes the CollectionPatientSummary class.

        Parameters:
            collections (proknow.Collections.Collections): The Collections instance that is
                instantiating the object.
            summary (dict): A dictionary representing the collection patient summary as returned by
                the API.
        """
        self._collections = collections
        self._proknow = self._collections._proknow
        self._data = summary
        self._id = summary["patient"]["id"]
        if summary["entity"] is None:
            self._entity_id = None
        else:
            self._entity_id = summary["entity"]["id"]

    @property
    def id(self):
        return self._id

    @property
    def entity_id(self):
        return self._entity_id

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the patient.

        Returns:
            :class:`proknow.Patients.PatientItem`: An object representing a patient in the
            organization.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of CollectionPatientSummary objects
            into a list of PatientItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name="My Collection").get()
                patients = [patient.get() for patient in collection.patients.query()]
        """
        return self._proknow.patients.get(self._data["workspace"]["id"], self._data["patient"]["id"])
