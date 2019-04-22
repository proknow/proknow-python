from .Scorecards import EntityScorecards


class EntityItem(object):
    """

    This class is a base class for specific entity types.

    Attributes:
        id (str): The id of the entity (readonly).
        workspace_id (str): The id of the workspace (readonly).
        patient_id (str): The id of the patient (readonly).
        data (dict): The complete representation of the entity as returned from the API (readonly).

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
        self.scorecards = EntityScorecards(patients, workspace_id, self._id)

    @property
    def id(self):
        return self._id

    @property
    def workspace_id(self):
        return self._workspace_id

    @property
    def patient_id(self):
        return self._patient_id

    @property
    def data(self):
        return self._data
