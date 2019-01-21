__all__ = [
    'Patients',
]

import os
import six


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

    def create(self, workspace, mrn, name, birth_date=None, birth_time=None, sex=None):
        """Creates a new patient.

        Parameters:
            workspace (str): An id or name of the workspace in which to create the patient.
            mrn (str): The MRN of the patient.
            name (str): The name of the patient.
            birth_date (str, optional): The birth date of the patient.
            birth_time (str, optional): The birth time of the patient.
            sex (str, optional): The sex of the patient.

        Returns:
            :class:`proknow.Patients.PatientItem`: A representation of the created patient.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(workspace, six.string_types), "`workspace` is required as a string."
        assert isinstance(mrn, str), "`mrn` is required as a string."
        assert isinstance(name, str), "`name` is required as a string."
        if birth_date is not None:
            assert isinstance(birth_date, str), "`birth_date` is required as a string."
        if birth_time is not None:
            assert isinstance(birth_time, str), "`birth_time` is required as a string."
        if sex is not None:
            assert isinstance(sex, str), "`sex` is required as a string."


        item = self._proknow.workspaces.resolve(workspace)

        body = {
            "mrn": mrn,
            "name": name,
            "birth_date": birth_date,
            "birth_time": birth_time,
            "sex": sex,
        }

        _, patient = self._requestor.post('/workspaces/' + item.id + '/patients', body=body)
        return PatientItem(self, patient)

    def delete(self, workspace_id, patient_id):
        """Deletes a patient.

        Parameters:
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
        """
        assert isinstance(workspace_id, six.string_types), "`workspace_id` is required as a string."
        assert isinstance(patient_id, six.string_types), "`patient_id` is required as a string."
        self._requestor.delete('/workspaces/' + workspace_id + '/patients/' + patient_id)

    def find(self, workspace, predicate=None, **props):
        """Finds the first patient that matches the input paramters.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.
            predicate (func): A function that is passed a metric as input and which should return
                a bool indicating whether the metric is a match.
            **props: A dictionary of keyword arguments that may include any patient attribute.
                These arguments are considered in turn to find matching patients.

        Returns:
            :class:`proknow.Patients.PatientSummary`: A representation of the matching patient.
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
                return metric

        return None

    def lookup(self, workspace, mrns):
        """Looks up a collection of patients matching the given list of MRNs.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.
            mrns (list): A list of MRN string values.

        Returns:
            list: A list of :class:`proknow.Patients.PatientSummary` objects that match the given
            MRNs.
        """
        assert isinstance(workspace, six.string_types), "`workspace` is required as a string."

        item = self._proknow.workspaces.resolve(workspace)
        _, patients = self._requestor.post('/workspaces/' + item.id + '/patients/lookup', body=mrns)
        return [PatientSummary(self, item.id, patient) for patient in patients]

    def get(self, workspace_id, patient_id):
        """Gets a patient from the given workspace.

        Parameters:
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to get.

        Returns:
            :class:`proknow.Patients.PatientItem`: an object representing a patient in the
            organization
        """
        assert isinstance(workspace_id, six.string_types), "`workspace_id` is required as a string."
        assert isinstance(patient_id, six.string_types), "`patient_id` is required as a string."
        _, patient = self._requestor.get('/workspaces/' + workspace_id + '/patients/' + patient_id)
        return PatientItem(self, workspace_id, patient)

    def query(self, workspace):
        """Queries for patients.

        Parameters:
            workspace (str): An id or name of the workspace in which to query for patients.

        Returns:
            list: A list of :class:`proknow.Patients.PatientSummary` objects, each representing a
            summarized patient in the given workspace.
        """
        assert isinstance(workspace, six.string_types), "`workspace` is required as a string."

        item = self._proknow.workspaces.resolve(workspace)

        _, patients = self._requestor.get('/workspaces/' + item.id + '/patients')
        return [PatientSummary(self, item.id, patient) for patient in patients]

class PatientSummary(object):
    """

    This class represents a summary view of a patient. It's instantiated by the
    :meth:`proknow.Patients.Patients.query` method to represent each of the patients returned in a
    query result.

    Attributes:
        id (str): The id of the patient (readonly).
        mrn (str): The patient medical record number or MRN (readonly). In the Proknow interface,
            this is referred to as the Patient ID.
        name (str): The name of the patient (readonly).
        birth_date (str): The birth_date of the patient (readonly).
        birth_time (str): The birth_time of the patient (readonly).
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
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._id = patient["id"]
        self._mrn = patient["mrn"]
        self._name = patient["name"]
        self._birth_date = patient["birth_date"]
        self._birth_time = patient["birth_time"]
        self._sex = patient["sex"]
        self._data = patient

    @property
    def id(self):
        return self._id

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
    def birth_time(self):
        return self._birth_time

    @property
    def sex(self):
        return self._sex

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the patient.

        Returns:
            :class:`proknow.Patients.PatientItem`: an object representing a patient in the
            organization.
        """
        return self._patients.get(self._workspace_id, self._id)

class PatientItem(object):
    """

    This class represents a patient. It's instantiated by the :class:`proknow.Patients.Patients`
    class as a complete representation of a patient.

    Attributes:
        id (str): The id of the patient (readonly).
        data (dict): The complete representation of the patient as returned from the API (readonly).
        mrn (str): The MRN of the patient.
        name (str): The name of the patient.
        birth_date (str): The birth_date of the patient.
        birth_time (str): The birth_time of the patient.
        sex (str): The sex of the patient.
        metadata (dict): The metadata of the patient.
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
        self.birth_time = patient["birth_time"]
        self.sex = patient["sex"]
        self.metadata = patient["metadata"]
        self.studies = [StudySummary(self._patients, self._workspace_id, self._id, study) for study in patient["studies"]]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the patient."""
        self._patients.delete(self._workspace_id, self._id)

    def save(self):
        """Saves the changes made to a patient."""
        body = {
            "mrn": self.mrn,
            "name": self.name,
            "birth_date": self.birth_date,
            "birth_time": self.birth_time,
            "sex": self.sex,
            "metadata": self.metadata
        }
        _, patient = self._requestor.put('/workspaces/' + self._workspace_id + '/patients/' + self._id, body=body)
        self._data = patient
        self.mrn = patient["mrn"]
        self.name = patient["name"]
        self.birth_date = patient["birth_date"]
        self.birth_time = patient["birth_time"]
        self.sex = patient["sex"]
        self.metadata = patient["metadata"]
        self.studies = [StudySummary(self._patients, self._workspace_id, self._id, study) for study in patient["studies"]]

    def find_entities(self, predicate=None, **props):
        """Finds the entities for the patient matching the input paramters.

        Parameters:
            predicate (func): A function that is passed a entity as input and which should return
                a bool indicating whether the entity is a match.
            **props: A dictionary of keyword arguments that may include any entity attribute to
                match. These arguments are considered in turn to find matching entities.

        Returns:
            list: A list of matching :class:`proknow.Patients.EntitySummary` objects.
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
        """
        metadata = {}
        for key in self.metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            metadata[metric.name] = self.metadata[key]
        return metadata

    def set_metadata(self, metadata):
        """Sets the metadata dictionary to an encoded version of the given metadata dictionary.

        Params:
            metadata (dict): A dictionary of custom metric key-value pairs where the keys are the
            names of the custom metric.
        """
        encoded = {}
        for key in metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            encoded[metric.id] = metadata[key]
        self.metadata = encoded

class StudySummary(object):
    """

    This class represents a summary view of a study. It's instantiated by the
    :meth:`proknow.Patients.PatientItem` class to represent each of the studies that belong to the
    patient.

    Attributes:
        id (str): The id of the study (readonly).
        data (dict): The summary representation of the study as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, study):
        """Initializes the PatientItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the study belongs.
            study (dict): A dictionary of study attributes.
        """
        self._patients = patients
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = study["id"]
        self._data = study
        self.entities = [EntitySummary(self._patients, self._workspace_id, self._patient_id, entity) for entity in study["entities"]]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

class EntitySummary(object):
    """

    This class represents a summary view of an entity. It's instantiated by the
    :meth:`proknow.Patients.StudySummary` class to represent each of the entities that belong to the
    study.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the PatientItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        self._patients = patients
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = entity["id"]
        self._data = entity
        self.entities = [EntitySummary(self._patients, self._workspace_id, self._patient_id, entity) for entity in entity["entities"]]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the entity item for the entity summary type.

        Returns:
            One of (:class:`proknow.Patients.ImageSetItem`,
            :class:`proknow.Patients.StructureSetItem`, :class:`proknow.Patients.PlanItem`,
            :class:`proknow.Patients.DoseItem`) based on the entity summary type.
        """
        entity_type = self._data["type"]
        if entity_type == "image_set":
            _, image_set = self._requestor.get('/workspaces/' + self._workspace_id + '/imagesets/' + self._id)
            return ImageSetItem(self._patients, self._workspace_id, self._patient_id, image_set)
        elif entity_type == "structure_set":
            _, structure_set = self._requestor.get('/workspaces/' + self._workspace_id + '/structuresets/' + self._id)
            return StructureSetItem(self._patients, self._workspace_id, self._patient_id, structure_set)
        elif entity_type == "plan":
            _, plan = self._requestor.get('/workspaces/' + self._workspace_id + '/plans/' + self._id)
            return PlanItem(self._patients, self._workspace_id, self._patient_id, plan)
        elif entity_type == "dose":
            _, dose = self._requestor.get('/workspaces/' + self._workspace_id + '/doses/' + self._id)
            return DoseItem(self._patients, self._workspace_id, self._patient_id, dose)

class EntityItem(object):
    """

    This class is a base class for specific entity types.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the PatientItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        self._patients = patients
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = entity["id"]
        self._data = entity

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def _resolve_path(self, path):
        if os.path.isdir(path):
            entity_type = self._data["type"]
            if entity_type == 'image_set':
                # TODO: need to implement this
                # prefix = self._data["modality"]
                pass
            elif entity_type == 'structure_set':
                # TODO: need to implement this
                # prefix = "RS"
                pass
            elif entity_type == 'plan':
                prefix = "RP"
            elif entity_type == 'dose':
                prefix = "RD"
            return os.path.join(os.path.abspath(path), prefix + self._data["uid"] + ".dcm")
        else:
            return os.path.abspath(path)

class ImageSetItem(EntityItem):
    """Not implemented"""
    pass

class StructureSetItem(EntityItem):
    """Not implemented"""
    pass

class PlanItem(EntityItem):
    """

    This class represents a plan. It's instantiated by the :class:`proknow.Patients.EntitySummary`
    class as a complete representation of a plan entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the PlanItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        super(PlanItem, self).__init__(patients, workspace_id, patient_id, entity)

    def download(self, path):
        """Download the plan file.

        Parameters:
            path (str): A path to a directory or file to which the plan file should be streamed.
        """
        resolved_path = self._resolve_path(path)
        self._requestor.stream('/workspaces/' + self._workspace_id + '/plans/' + self._id + '/dicom', resolved_path)
        return resolved_path

class DoseItem(EntityItem):
    """

    This class represents a dose. It's instantiated by the :class:`proknow.Patients.EntitySummary`
    class as a complete representation of a dose entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the DoseItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        super(DoseItem, self).__init__(patients, workspace_id, patient_id, entity)

    def download(self, path):
        """Downloads the dose file.

        Parameters:
            path (str): A path to a directory or file to which the dose file should be streamed.
        """
        resolved_path = self._resolve_path(path)
        self._requestor.stream('/workspaces/' + self._workspace_id + '/doses/' + self._id + '/dicom', resolved_path)
        return resolved_path
