import time

from .ImageSets import ImageSetItem
from .StructureSets import StructureSetItem
from .Plans import PlanItem
from .Doses import DoseItem
from ...Exceptions import TimeoutExceededError


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
        count = 0
        DELAY = 0.2
        MAX_COUNT = 5 / DELAY
        if entity_type == "image_set":
            while True:
                _, image_set = self._requestor.get('/workspaces/' + self._workspace_id + '/imagesets/' + self._id)
                if image_set["status"] in ('completed', 'abstract'):
                    break
                else: # pragma: no cover (should not occur in normal circumstances)
                    if count < MAX_COUNT:
                        time.sleep(DELAY)
                        count += 1
                    else:
                        raise TimeoutExceededError('Timeout exceeded while waiting for image set entity to reach completed status')
            return ImageSetItem(self._patients, self._workspace_id, self._patient_id, image_set)
        elif entity_type == "structure_set":
            while True:
                _, structure_set = self._requestor.get('/workspaces/' + self._workspace_id + '/structuresets/' + self._id)
                if structure_set["status"] in ('completed', 'abstract'):
                    break
                else: # pragma: no cover (should not occur in normal circumstances)
                    if count < MAX_COUNT:
                        time.sleep(DELAY)
                        count += 1
                    else:
                        raise TimeoutExceededError('Timeout exceeded while waiting for structure set entity to reach completed status')
            return StructureSetItem(self._patients, self._workspace_id, self._patient_id, structure_set)
        elif entity_type == "plan":
            while True:
                _, plan = self._requestor.get('/workspaces/' + self._workspace_id + '/plans/' + self._id)
                if plan["status"] in ('completed', 'abstract'):
                    break
                else: # pragma: no cover (should not occur in normal circumstances)
                    if count < MAX_COUNT:
                        time.sleep(DELAY)
                        count += 1
                    else:
                        raise TimeoutExceededError('Timeout exceeded while waiting for plan entity to reach completed status')
            return PlanItem(self._patients, self._workspace_id, self._patient_id, plan)
        elif entity_type == "dose":
            while True:
                _, dose = self._requestor.get('/workspaces/' + self._workspace_id + '/doses/' + self._id)
                if dose["status"] in ('completed', 'abstract'):
                    break
                else: # pragma: no cover (should not occur in normal circumstances)
                    if count < MAX_COUNT:
                        time.sleep(DELAY)
                        count += 1
                    else:
                        raise TimeoutExceededError('Timeout exceeded while waiting for dose entity to reach completed status')
            return DoseItem(self._patients, self._workspace_id, self._patient_id, dose)
        else: # pragma: no cover (included for completeness)
            assert entity_type in ("image_set", "structure_set", "plan", "dose"), 'Expected the entity type to be one of ("image_set", "structure_set", "plan", "dose")'

    def delete(self):
        """Deletes the entity.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This examples shows how you can delete the entities within a patient while leaving the
            patient intact::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(lambda entity: True)
                for entity in entities:
                    entity.delete()
        """
        self._requestor.delete('/workspaces/' + self._workspace_id + '/entities/' + self._id)
