import six

from .ImageSets import ImageSetItem
from .StructureSets import StructureSetItem
from .Plans import PlanItem
from .Doses import DoseItem


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

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            Use this example to find all of the patient's entities and construct a list of the
            type-specific object types::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = [entity.get() for entity in patient.find_entities(lambda entity: True)]
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
