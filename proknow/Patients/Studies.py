from .Entities import EntitySummary


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
