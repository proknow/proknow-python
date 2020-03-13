import os
import six
import datetime

from .EntityItem import EntityItem
from ...Exceptions import InvalidPathError


class PlanItem(EntityItem):
    """

    This class represents a plan. It's instantiated by the :class:`proknow.Patients.EntitySummary`
    class as a complete representation of a plan entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The complete representation of the entity as returned from the API (readonly).

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

    def _wait_delivery_information(self):
        start = datetime.datetime.now()
        DELAY = 0.2
        while (datetime.datetime.now() - start).total_seconds() < self._proknow.ENTITY_WAIT_TIMEOUT:
            entity_status = self.data["status"]
            if entity_status == 'completed':
                return
            else: # pragma: no cover (unreliable)
                time.sleep(DELAY)
                _, plan = self._requestor.get('/workspaces/' + self._workspace_id + '/plans/' + self._id)
                self._update(plan)
        raise TimeoutExceededError('Timeout exceeded while waiting for delivery information to reach completed status') # pragma: no cover (should not occur in normal circumstances)

    def download(self, path):
        """Download the plan file.

        Parameters:
            path (str): A path to a directory or file to which the plan file should be streamed.

        Returns:
            str: The absolute path to the downloaded file.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided path is invalid.

        Example:
            This example shows how to download a plan file for a patient to the current directory::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="plan")
                plan = entities[0].get()
                plan.download("./")
        """
        assert isinstance(path, six.string_types), "`path` is required as a string."
        if os.path.isdir(path):
            resolved_path = os.path.join(os.path.abspath(path), "RP." + self._data["uid"] + ".dcm")
        else:
            absolute = os.path.abspath(path)
            directory = os.path.dirname(path)
            if os.path.isdir(directory):
                resolved_path = absolute
            else:
                raise InvalidPathError('`' + path + '` is invalid')
        self._requestor.stream('/workspaces/' + self._workspace_id + '/plans/' + self._id + '/dicom', resolved_path)
        return resolved_path

    def get_delivery_information(self):
        """Gets the delivery information for the plan.

        The delivery information is returned as a dictionary with keys including ``"equipment"``,
        ``"patient_setups"``, ``"fraction_groups"``, ``"beams"``, and ``"brachy"``.

        Returns:
            dict: The plan delivery information.

        Raises:
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the delivery information to become available.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to get the delivery information for a plan::
                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="plan")
                plan = entities[0].get()
                info = plan.get_delivery_information()
        """
        self._wait_delivery_information()
        headers = {
            'ProKnow-Key': self.data["key"]
        }
        _, content = self._requestor.get('/plans/' + self._id + '/delivery/' + self._data["data"]["delivery_tag"], headers=headers)
        return content

    def refresh(self):
        """Refreshes the plan entity.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to refresh a plan entity::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="plan")
                plan = entities[0].get()
                plan.refresh()
        """
        _, plan = self._requestor.get('/workspaces/' + self._workspace_id + '/plans/' + self._id)
        self._update(plan)
