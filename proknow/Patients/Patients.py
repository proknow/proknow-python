from datetime import datetime

from .Scorecards import PatientScorecards
from .Studies import StudySummary
from .Tasks import Tasks, TaskSummary, TaskItem


class Patients(object):
    """

    This class should be used to interact with the patients in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Patients class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def _query(self, workspace, query):
        res, data = self._requestor.get('/workspaces/' + workspace.id + '/patients', params=query)
        if res.headers['proknow-has-more'] == 'true': # pragma: no cover (difficult to test w/o lg num of patients)
            next_query = dict(query)
            next_query['page_epoch'] = res.headers['proknow-epoch']
            next_query["page_number"] = res.headers['proknow-next-page']
            return data + self._query(workspace, next_query)
        else:
            return data

    def create(self, workspace, mrn, name, birth_date=None, sex=None):
        """Creates a new patient.

        Parameters:
            workspace (str): An id or name of the workspace in which to create the patient.
            mrn (str): The MRN of the patient.
            name (str): The name of the patient.
            birth_date (str, optional): The birth date of the patient. If provided, this should be
                of the form ``"YYYY-MM-DD"`` or ``None``.
            sex (str, optional): The sex of the patient. This should be one of ``"M"``, ``"F"``,
                ``"O"``, or ``None``.

        Returns:
            :class:`proknow.Patients.PatientItem`: A representation of the created patient.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.

        Example:
            This example shows how to create a patient in the workspace called "Clinical"::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.create("Clinical", "12345", "Becker^Matthew")
        """
        assert isinstance(workspace, str), "`workspace` is required as a string."
        assert isinstance(mrn, str), "`mrn` is required as a string."
        assert isinstance(name, str), "`name` is required as a string."
        if birth_date is not None:
            assert isinstance(birth_date, str), "`birth_date` is required as a string."
        if sex is not None:
            assert isinstance(sex, str), "`sex` is required as a string."

        item = self._proknow.workspaces.resolve(workspace)

        body = {
            "mrn": mrn,
            "name": name,
            "birth_date": birth_date,
            "sex": sex,
        }

        _, patient = self._requestor.post('/workspaces/' + item.id + '/patients', json=body)
        return PatientItem(self, item.id, patient)

    def delete(self, workspace_id, patient_id):
        """Deletes a patient.

        Parameters:
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the workspace id and patient id, you can delete a patient directly using
            this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.patients.delete('5c463a6c040040f1efda74db75c1b121', '5c4b4c52a5c058c3d1d98ac194d0200f')
        """
        assert isinstance(workspace_id, str), "`workspace_id` is required as a string."
        assert isinstance(patient_id, str), "`patient_id` is required as a string."
        self._requestor.delete('/workspaces/' + workspace_id + '/patients/' + patient_id)

    def find(self, workspace, predicate=None, **props):
        """Finds the first patient that matches the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.
            predicate (func): A function that is passed a metric as input and which should return
                a bool indicating whether the metric is a match.
            **props: A dictionary of keyword arguments that may include any patient attribute.
                These arguments are considered in turn to find matching patients.

        Returns:
            :class:`proknow.Patients.PatientSummary`: A representation of the matching patient.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.
        """
        patients = self.query(workspace)
        if predicate is None and len(props) == 0:
            return None

        for patient in patients:
            match = True
            if predicate is not None and not predicate(patient):
                match = False
            for key in props:
                if patient._data[key] != props[key]:
                    match = False
            if match:
                return patient

        return None

    def lookup(self, workspace, mrns):
        """Looks up a collection of patients matching the given list of MRNs.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.
            mrns (list): A list of MRN string values.

        Returns:
            list: A list of :class:`proknow.Patients.PatientSummary` objects that match the given
            MRNs. If the mrn at a given index cannot be found, the result will contain the value
            None at that index.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.

        Example:
            Use this method to resolve a list of patient MRNs. Just provide the ID as a list in the
            second argument::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.patients.lookup('Clinical', ['HNC-0522c0009', 'HNC-0522c0013'])
        """
        assert isinstance(workspace, str), "`workspace` is required as a string."

        item = self._proknow.workspaces.resolve(workspace)
        _, patients = self._requestor.post('/workspaces/' + item.id + '/patients/lookup', json=mrns)
        return [PatientSummary(self, item.id, patient) if patient != None else None for patient in patients]

    def get(self, workspace_id, patient_id):
        """Gets a patient from the given workspace.

        Parameters:
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to get.

        Returns:
            :class:`proknow.Patients.PatientItem`: An object representing a patient in the
            organization

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the workspace id and patient id, you can get the patient directly using
            this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.patients.get('5c463a6c040040f1efda74db75c1b121', '5c4b4c52a5c058c3d1d98ac194d0200f')
        """
        assert isinstance(workspace_id, str), "`workspace_id` is required as a string."
        assert isinstance(patient_id, str), "`patient_id` is required as a string."
        _, patient = self._requestor.get('/workspaces/' + workspace_id + '/patients/' + patient_id)
        return PatientItem(self, workspace_id, patient)

    def query(self, workspace, search=None):
        """Queries for patients.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.
            search (str, optional): If provided, returns only the patients whose MRN or name match
                the parameter.

        Returns:
            list: A list of :class:`proknow.Patients.PatientSummary` objects, each representing a
            summarized patient in the given workspace.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the patients belonging to the Clinical workspace and prints the
            name of each patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                for patient in pk.patients.query("Clinical"):
                    print(patient.name)
        """
        assert isinstance(workspace, str), "`workspace` is required as a string."

        item = self._proknow.workspaces.resolve(workspace)
        query = {}
        if search is not None:
            query["search"] = search
        return [PatientSummary(self, item.id, patient) for patient in self._query(item, query)]

class PatientSummary(object):
    """

    This class represents a summary view of a patient. It's instantiated by the
    :meth:`proknow.Patients.Patients.query` method to represent each of the patients returned in a
    query result.

    Attributes:
        id (str): The id of the patient (readonly).
        workspace_id (str): The id of the workspace in which the patient belongs (readonly).
        mrn (str): The patient medical record number or MRN (readonly). In the Proknow interface,
            this is referred to as the Patient ID.
        name (str): The name of the patient (readonly).
        birth_date (str): The birth_date of the patient (readonly).
        sex (str): The sex of the patient (readonly).
        data (dict): The summary representation of the patient as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient):
        """Initializes the PatientSummary class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient (dict): A dictionary of patient attributes.
        """
        self._patients = patients
        self._proknow = self._patients._proknow
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._id = patient["id"]
        self._mrn = patient["mrn"]
        self._name = patient["name"]
        self._birth_date = patient["birth_date"]
        self._sex = patient["sex"]
        self._data = patient

    @property
    def id(self):
        return self._id

    @property
    def workspace_id(self):
        return self._workspace_id

    @property
    def mrn(self):
        return self._mrn

    @property
    def name(self):
        return self._name

    @property
    def birth_date(self):
        return self._birth_date

    @property
    def sex(self):
        return self._sex

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
            The following example shows how to turn a list of PatientSummary objects into a list of
            PatientItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = [patient.get() for patient in pk.patients.query("Clinical")]
        """
        return self._patients.get(self._workspace_id, self._id)

    def upload(self, path_or_paths, **kwargs):
        """Initiates an upload or series of uploads to the API for a patient.

        Parameters:
            path_or_paths (str or list): A path or list of paths such that each path is a directory
                of files to upload or a path to a file to upload.
            **kwargs: Keyword arguments to be passed along to the
                :meth:`proknow.Uploads.Uploads.upload` method.

        Returns:
            :class:`proknow.Uploads.UploadBatch`: An object used to manage a batch of uploads.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided file path is invalid.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the uploads to complete.

        Example:
            This examples show how to upload a directory of files to a patient::

                from proknow import ProKnow
                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.lookup('Clinical', ['HNC-0522c0009'])[0]
                patient.upload("./DICOM")
        """
        kwargs["overrides"] = {
            "patient": {
                "mrn": self._mrn,
                "name": self._name,
                "birth_date": self._birth_date,
                "sex": self._sex,
            },
        }
        return self._proknow.uploads.upload(self._workspace_id, path_or_paths, **kwargs)

class PatientItem(object):
    """

    This class represents a patient. It's instantiated by the :class:`proknow.Patients.Patients`
    class as a complete representation of a patient.

    Attributes:
        id (str): The id of the patient (readonly).
        workspace_id (str): The id of the workspace in which the patient belongs (readonly).
        data (dict): The complete representation of the patient as returned from the API (readonly).
        mrn (str): The MRN of the patient.
        name (str): The name of the patient.
        birth_date (str): The birth_date of the patient.
        sex (str): The sex of the patient.
        metadata (dict): The metadata of the patient.
        scorecards (proknow.Patients.PatientScorecards): An object for interacting with the
            scorecards belonging to the entity.
        studies (list): A list of :class:`proknow.Patients.StudySummary` objects for the patient.
        tasks (:class:`proknow.Patients.Tasks`): An instance of the Tasks class for the patient.
    """

    def __init__(self, patients, workspace_id, patient):
        """Initializes the PatientItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient (dict): A dictionary of patient attributes.
        """
        self._patients = patients
        self._proknow = self._patients._proknow
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._id = patient["id"]
        self._data = patient
        self.mrn = patient["mrn"]
        self.name = patient["name"]
        self.birth_date = patient["birth_date"]
        self.sex = patient["sex"]
        self.metadata = patient["metadata"]
        self.scorecards = PatientScorecards(self._patients, self._workspace_id, self._id)
        self.studies = [StudySummary(self._patients, self._workspace_id, self._id, study) for study in patient["studies"]]
        self.tasks = Tasks(self._patients, self._workspace_id, self._id)

    @property
    def id(self):
        return self._id

    @property
    def workspace_id(self):
        return self._workspace_id

    @property
    def data(self):
        return self._data

    def create_plan(self, name, image_set_id=None, structure_set_id=None, dose_id=None):
        """Creates a structure set.

        Parameters:
            name (str): The name of the structure set (available as the entity description).
            image_set_id (str, optional): The id of the image set.
            structure_set_id (str, optional): The id of the structure set.
            dose_id (str, optional): The id of the dose.

        Returns:
            :class:`proknow.Patients.EntitySummary`: The entity summary object representing the new
            plan.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to create a plan::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                image_set = patient.find_entities(modality="CT")[0]
                plan = patient.create_plan("My Plan", image_set_id=image_set.id)
        """
        body = {
            "name": name,
        }
        if image_set_id is not None:
            body["image_set_id"] = image_set_id
        elif structure_set_id is not None:
            body["structure_set_id"] = structure_set_id
        elif dose_id is not None:
            body["dose_id"] = dose_id
        else:
            assert image_set_id is not None or structure_set_id is not None or dose_id is not None, "One of (image_set_id, structure_set_id, dose_id) is required"
        _, result = self._requestor.post('/workspaces/' + self._workspace_id + '/plans', json=body)
        self.refresh()
        entities = self.find_entities(id=result["id"])
        assert len(entities) == 1, "Problem finding created plan"
        return entities[0]

    def create_structure_set(self, name, image_set_id):
        """Creates a structure set.

        Parameters:
            name (str): The name of the structure set (available as the entity description).
            image_set_id (str): The id of the image set.

        Returns:
            :class:`proknow.Patients.EntitySummary`: The entity summary object representing the new
            structure set.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to create a structure set::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                image_set = patient.find_entities(modality="CT")[0]
                structure_set = patient.create_structure_set("My Structure Set", image_set.id)
        """
        body = {
            "name": name,
            "image_set_id": image_set_id,
        }
        _, result = self._requestor.post('/workspaces/' + self._workspace_id + '/structuresets', json=body)
        self.refresh()
        entities = self.find_entities(id=result["id"])
        assert len(entities) == 1, "Problem finding created structure set"
        return entities[0]

    def delete(self):
        """Deletes the patient.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a patient by its MRN and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                patient.delete()
        """
        self._patients.delete(self._workspace_id, self._id)

    def save(self):
        """Saves the changes made to a patient.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a patient by its MRN, update the name, and save
            it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                patient.name = "ANON-1234"
                patient.save()
        """
        body = {
            "mrn": self.mrn,
            "name": self.name,
            "birth_date": self.birth_date,
            "sex": self.sex,
            "metadata": self.metadata
        }
        _, patient = self._requestor.put('/workspaces/' + self._workspace_id + '/patients/' + self._id, json=body)
        self._data = patient
        self.mrn = patient["mrn"]
        self.name = patient["name"]
        self.birth_date = patient["birth_date"]
        self.sex = patient["sex"]
        self.metadata = patient["metadata"]
        self.studies = [StudySummary(self._patients, self._workspace_id, self._id, study) for study in patient["studies"]]

    def find_entities(self, predicate=None, **props):
        """Finds the entities for the patient matching the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Parameters:
            predicate (func): A function that is passed an entity as input and which should return
                a bool indicating whether the entity is a match.
            **props: A dictionary of keyword arguments that may include any entity attribute to
                match. These arguments are considered in turn to find matching entities.

        Returns:
            list: A list of matching :class:`proknow.Patients.EntitySummary` objects.

        Example:
            Use this example to find the patient entities matching the predicate function (returns
            all plan and dose entities)::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(lambda entity: entity.data["type"] == "dose" or entity.data["type"] == "plan")

            Use this example to find the patient entities matching the predicate function (returns
            entities with the modality value of "MR")::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(modality="MR")
        """
        if predicate is None and len(props) == 0:
            return []

        entities = []
        for study in self.studies:
            for entity_i in study.entities:
                match_i = True
                for key in props:
                    if entity_i.data[key] != props[key]:
                        match_i = False
                if predicate is not None and not predicate(entity_i):
                    match_i = False
                if match_i:
                    entities.append(entity_i)

                for entity_j in entity_i.entities:
                    match_j = True
                    for key in props:
                        if entity_j.data[key] != props[key]:
                            match_j = False
                    if predicate is not None and not predicate(entity_j):
                        match_j = False
                    if match_j:
                        entities.append(entity_j)

                    for entity_k in entity_j.entities:
                        match_k = True
                        for key in props:
                            if entity_k.data[key] != props[key]:
                                match_k = False
                        if predicate is not None and not predicate(entity_k):
                            match_k = False
                        if match_k:
                            entities.append(entity_k)

                        for entity_m in entity_k.entities:
                            match_m = True
                            for key in props:
                                if entity_m.data[key] != props[key]:
                                    match_m = False
                            if predicate is not None and not predicate(entity_m):
                                match_m = False
                            if match_m:
                                entities.append(entity_m)
        return entities

    def get_metadata(self):
        """Gets the metadata dictionary and decodes the ids into metrics names.

        Returns:
            dict: The dictionary of custom metric key-value pairs where the keys are the decoded
            custom metric names.

        Raises:
            :class:`proknow.Exceptions.CustomMetricLookupError`: If a custom metric could not be
                resolved.

        Example:
            Use this example to print the metadata values for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                for key, value in patient.get_metadata():
                    print(key + ": " + value)
        """
        metadata = {}
        for key in self.metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            metadata[metric.name] = self.metadata[key]
        return metadata

    def refresh(self):
        """Refreshes the patient state.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to refresh the patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                patient.refresh()
        """
        _, patient = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._id)
        self._data = patient
        self.mrn = patient["mrn"]
        self.name = patient["name"]
        self.birth_date = patient["birth_date"]
        self.sex = patient["sex"]
        self.metadata = patient["metadata"]
        self.studies = [StudySummary(self._patients, self._workspace_id, self._id, study) for study in patient["studies"]]
        self.tasks = Tasks(self._patients, self._workspace_id, self._id)

    def set_metadata(self, metadata):
        """Sets the metadata dictionary to an encoded version of the given metadata dictionary.

        Parameters:
            metadata (dict): A dictionary of custom metric key-value pairs where the keys are the
                names of the custom metric.

        Raises:
            :class:`proknow.Exceptions.CustomMetricLookupError`: If a custom metric could not be
                resolved.

        Example:
            Use this example to set the metadata value for "Genetic Type" for a patient before
            saving::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                meta = patient.get_metadata()
                meta["Genetic Type"] = "Type II"
                patient.set_metadata(meta)
                patient.save()

        """
        encoded = {}
        for key in metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            encoded[metric.id] = metadata[key]
        self.metadata = encoded

    def upload(self, path_or_paths, **kwargs):
        """Initiates an upload or series of uploads to the API for a patient.

        Parameters:
            path_or_paths (str or list): A path or list of paths such that each path is a directory
                of files to upload or a path to a file to upload.
            **kwargs: Keyword arguments to be passed along to the
                :meth:`proknow.Uploads.Uploads.upload` method.

        Returns:
            :class:`proknow.Uploads.UploadBatch`: An object used to manage a batch of uploads.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided file path is invalid.
            :class:`proknow.Exceptions.WorkspaceLookupError`: If the workspace with the given
                name or id could not be found.
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the uploads to complete.

        Example:
            This example shows how to upload a directory of files to a patient::

                from proknow import ProKnow
                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup('Clinical', ['HNC-0522c0009'])
                patient = patients[0].get()
                patient.upload("./DICOM")
        """
        kwargs["overrides"] = {
            "patient": {
                "mrn": self.mrn,
                "name": self.name,
                "birth_date": self.birth_date,
                "sex": self.sex,
            },
        }
        kwargs["scope"] = self._id
        return self._proknow.uploads.upload(self._workspace_id, path_or_paths, **kwargs)
