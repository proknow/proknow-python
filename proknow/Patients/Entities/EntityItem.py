import six

from .Scorecards import EntityScorecards


class EntityItem(object):
    """

    This class is a base class for specific entity types.

    Attributes:
        id (str): The id of the entity (readonly).
        workspace_id (str): The id of the workspace (readonly).
        patient_id (str): The id of the patient (readonly).
        data (dict): The complete representation of the entity as returned from the API (readonly).
        description (str): The entity description.
        metadata (dict): The entity metadata.
        scorecards (proknow.Patients.EntityScorecards): An object for interacting with the
            scorecards belonging to the entity.

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
        self._proknow = self._patients._proknow
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._update(entity)
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

    def _update(self, entity):
        self._id = entity["id"]
        self._data = entity
        self.description = entity["description"]
        self.metadata = entity["metadata"]

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
                    entity.get().delete()
        """
        self._requestor.delete('/workspaces/' + self._workspace_id + '/entities/' + self._id)

    def get_metadata(self):
        """Gets the metadata dictionary and decodes the ids into metrics names.

        Returns:
            dict: The dictionary of custom metric key-value pairs where the keys are the decoded
            custom metric names.

        Raises:
            :class:`proknow.Exceptions.CustomMetricLookupError`: If a custom metric could not be
                resolved.

        Example:
            Use this example to print the metadata values for a patient entity::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                dose_summary = patient.find_entities(type="dose")[0]
                dose = dose_summary.get()
                meta = dose.get_metadata()
                print(meta)
        """
        metadata = {}
        for key in self.metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            metadata[metric.name] = self.metadata[key]
        return metadata

    def save(self):
        """Saves the changes made to an entity.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a dose, update its description, and save it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                dose_summary = patient.find_entities(type="dose")[0]
                dose = dose_summary.get()
                dose.description = "Summed"
                dose.save()
        """
        body = {
            "description": self.description,
            "metadata": self.metadata
        }
        _, entity = self._requestor.put('/workspaces/' + self._workspace_id + '/entities/' + self._id, json=body)
        self._data = entity
        self.description = entity["description"]
        self.metadata = entity["metadata"]

    def set_metadata(self, metadata):
        """Sets the metadata dictionary to an encoded version of the given metadata dictionary.

        Parameters:
            metadata (dict): A dictionary of custom metric key-value pairs where the keys are the
            names of the custom metric.

        Raises:
            :class:`proknow.Exceptions.CustomMetricLookupError`: If a custom metric could not be
                resolved.

        Example:
            Use this example to set the metadata value for "Algorithm" for a dose entity before
            saving::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                dose_summary = patient.find_entities(type="dose")[0]
                dose = dose_summary.get()
                meta = dose.get_metadata()
                meta["Algorithm"] = "Monte Carlo"
                dose.set_metadata(meta)
                dose.save()

        """
        encoded = {}
        for key in metadata:
            metric = self._proknow.custom_metrics.resolve(key)
            encoded[metric.id] = metadata[key]
        self.metadata = encoded

    def update_parent(self, entity):
        """Update the parent of the entity.

        Parameters:
            entity (:class:`proknow.Patients.EntitySummary`, :class:`proknow.Patients.EntityItem`, str):
                An entity-like object or a entity id to be used to set the new parent of the entity.

        Raises:
            AttributeError: If the provided object is not an entity-like object.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            Use this example to update the parent of the dose entity to be the structure set::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                dose_summary = patient.find_entities(type="dose")[0]
                structure_set_summary = patient.find_entities(type="structure_set")[0]
                dose = dose_summary.get()
                dose.update_parent(structure_set_summary)
        """
        if isinstance(entity, six.string_types):
            parent_id = entity
        else:
            parent_id = entity.id
        self._requestor.put('/workspaces/' + self._workspace_id + '/entities/' + self._id + '/parent/' + parent_id)
        self.refresh()
