import os
import six
from time import sleep
from datetime import datetime, timedelta
from threading import Timer

from .EntityItem import EntityItem
from ...Exceptions import InvalidOperationError, InvalidPathError, TimeoutExceededError, HttpError


class StructureSetDraftLockRenewer(object):
    """

    This class is responsible for keeping the structure set lock from expiring.

    """

    def __init__(self, structure_set):
        """Initializes the StructureSetDraftLockRenewer class.

        Note that the lock renewal will occur according to the timeout set for the
        ``LOCK_RENEWAL_BUFFER``. See :class:`proknow.Patients` for more information.

        Parameters:
            structure_set (proknow.Patients.StructureSetItem): The stucture set with the lock to
                keep from expiring
        """
        self._structure_set = structure_set
        self._workspace_id = structure_set.workspace_id
        self._LOCK_RENEWAL_BUFFER = self._structure_set._patients._proknow.LOCK_RENEWAL_BUFFER
        self._requestor = structure_set._requestor
        self._timer = None
        self._started = False

    def _run(self):
        """A helper function used to perform the lock renewal"""
        wid = self._workspace_id
        sid = self._structure_set._id
        lid = self._structure_set._lock["id"]
        _, lock = self._requestor.put('/workspaces/' + wid + '/structuresets/' + sid + '/draft/lock/' + lid)
        self._structure_set._lock = lock

    def start(self):
        """Starts the lock renewal timer in the background."""
        if not self._started:
            expires = datetime.strptime(self._structure_set._lock["expires_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            diff = expires - datetime.utcnow() - timedelta(seconds=self._LOCK_RENEWAL_BUFFER)
            self._timer = Timer(diff.total_seconds(), self._run)
            self._timer.start()
            self._started = True

    def stop(self):
        """Stops the lock renewal timer."""
        if self._started:
            self._timer.cancel()
            self._started = False

class StructureSetItem(EntityItem):
    """

    This class represents a structure set. It's instantiated by the
    :class:`proknow.Patients.EntitySummary` class as a complete representation of a structure set
    entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The complete representation of the entity as returned from the API (readonly).
        rois (list): A list of :class:`proknow.Patients.StructureSetRoiItem` items.
        versions (:class:`proknow.Patients.StructureSetVersions`): A object for interacting with the
            versions of the current structure set.

    """

    def __init__(self, patients, workspace_id, patient_id, entity, lock=None, is_editable=False, is_draft=False):
        """Initializes the StructureSetItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        super(StructureSetItem, self).__init__(patients, workspace_id, patient_id, entity)
        self._is_editable = is_editable
        self._is_draft = is_draft
        self._lock = lock
        self._renewer = None
        self.rois = [StructureSetRoiItem(self, roi) for roi in entity["data"]["rois"]]
        self.versions = StructureSetVersions(self)

    def __enter__(self):
        self.start_renewer()
        return self

    def __exit__(self, type, value, traceback):
        self.stop_renewer()
        self.release_lock()

    def is_draft(self):
        """Returns whether the structure set item is a draft.

        Returns:
            bool: True if the structure set item is a draft and False otherwise
        """
        return self._is_draft

    def is_editable(self):
        """Returns whether the structure set item is editable.

        Returns:
            bool: True if the structure set item is editable and False otherwise
        """
        return self._is_editable

    def approve(self, label=None, message=None):
        """Approves the draft structure set.

        Parameters:
            label (str, optional): The label for the new structure set version.
            message (str, optional): The message for the new structure set version.

        Returns:
            :class:`proknow.Patients.StructureSetItem`: The newly approved structure set item.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example shows how to approve a draft version of a structure set (with no other
            changes)::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                with structure_set.draft() as draft:
                    draft.approve()
        """
        if not self._is_editable:
            raise InvalidOperationError('Item is not editable')
        if label is not None:
            assert isinstance(label, six.string_types), "`label`, if provided, must be a string"
        if message is not None:
            assert isinstance(message, six.string_types), "`message`, if provided, must be a string"
        wid = self._workspace_id
        sid = self._id
        headers = { 'ProKnow-Lock': self._lock["id"] }
        body = {
            "version": self._data["data"]["version"],
            "rois": [{ "id": roi.id, "tag": roi.tag } for roi in self.rois],
            "label": label,
            "message": message
        }
        self._requestor.post('/workspaces/' + wid + '/structuresets/' + sid + '/draft/approve', body=body, headers=headers)
        self.stop_renewer()
        self._is_editable = False
        self._is_draft = False
        self._lock = None
        return self.versions.get("approved")

    def create_roi(self, name, color, type):
        """Creates a new ROI as part of the draft structure set.

        Parameters:
            name (str): The name of the new ROI.
            color (list): The color of the new ROI.
            type (str): The type of the new ROI (todo: link here).

        Returns:
            :class:`proknow.Patients.StructureSetRoiItem`: The item created as part of the draft
            structure set.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example shows how to add a new ROI for PTV::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                with structure_set.draft() as draft:
                    draft.create_roi("PTV", [255, 0, 0], "PTV")
        """
        if not self._is_editable:
            raise InvalidOperationError('Item is not editable')
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(color, list) or len(color) != 3, "`color` is required as a list of size 3"
        assert isinstance(type, six.string_types), "`type` is required as a string."
        headers = { 'ProKnow-Lock': self._lock["id"] }
        body = {
            "name": name,
            "color": color,
            "type": type
        }
        wid = self._workspace_id
        sid = self._id
        _, roi = self._requestor.post('/workspaces/' + wid + '/structuresets/' + sid + '/draft/rois', body=body, headers=headers)
        roi_item = StructureSetRoiItem(self, roi)
        self.rois.append(roi_item)
        return roi_item

    def discard(self):
        """Discuards the draft structure set.

        Parameters:
            name (str): The name of the new ROI.
            color (list): The color of the new ROI.
            type (str): The type of the new ROI (todo: link here).

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example loads the current draft and discards it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                with structure_set.draft() as draft:
                    draft.discard()
        """
        if not self._is_editable:
            raise InvalidOperationError('Item is not editable')
        wid = self._workspace_id
        sid = self._id
        headers = { 'ProKnow-Lock': self._lock["id"] }
        body = {
            "version": self._data["data"]["version"],
            "rois": [{ "id": roi.id, "tag": roi.tag } for roi in self.rois]
        }
        self._requestor.post('/workspaces/' + wid + '/structuresets/' + sid + '/draft/discard', body=body, headers=headers)
        self.stop_renewer()
        self._is_editable = False
        self._lock = None

    def download(self, path):
        """Download the current structure set file.

        Parameters:
            path (str): A path to a directory or file to which the structure set file should be
            streamed.

        Returns:
            str: The absolute path to the downloaded file.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided path is invalid.

        Example:
            This example shows how to download a structure set file for a patient to the current
            directory::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                structure_set.download("./")
        """
        if self._is_draft:
            raise InvalidOperationError('Draft versions of structure sets cannot be downloaded')
        assert isinstance(path, six.string_types), "`path` is required as a string."
        if os.path.isdir(path):
            resolved_path = os.path.join(os.path.abspath(path), "RS." + self._data["uid"] + ".dcm")
        else:
            absolute = os.path.abspath(path)
            directory = os.path.dirname(path)
            if os.path.isdir(directory):
                resolved_path = absolute
            else:
                raise InvalidPathError('`' + path + '` is invalid')
        wid = self._workspace_id
        sid = self._id
        self._requestor.stream('/workspaces/' + wid + '/structuresets/' + sid + '/versions/' + self._data["data"]["version"] + '/dicom', resolved_path)
        return resolved_path

    def draft(self):
        """Creates a draft if one does not already exist for the structure set or obtains the lock.

        Returns:
            :class:`proknow.Patients.StructureSetItem`: A draft structure set item.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            It is usually best to use ``with`` statements to obtain a draft of a structure set,
            which will allow the SDK to manage lock renewal for you::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                with structure_set.draft() as draft:
                    pass # Your code here

            Of course, it's possible to create a draft without using the built-in context management
            functionality, but be aware that you will have to manage the renewal of structure set
            draft locks yourself::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                draft = structure_set.draft()
                draft.start_renewer()
                try:
                    # Do something with the draft here...
                finally:
                    draft.stop_renewer()
                    draft.release_lock()

        """
        wid = self._workspace_id
        sid = self._id
        try:
            _, lock = self._requestor.post('/workspaces/' + wid + '/structuresets/' + sid + '/draft')
        except HttpError as err:
            if err.status_code != 409:
                raise err
            _, lock = self._requestor.get('/workspaces/' + wid + '/structuresets/' + sid + '/draft/lock')
        query = { 'version': 'draft' }
        _, structure_set = self._requestor.get('/workspaces/' + wid + '/structuresets/' + sid, query=query)
        return StructureSetItem(self._patients, wid, self._patient_id, structure_set, lock=lock, is_draft=True, is_editable=True)

    def release_lock(self):
        """Releases the lock for the draft structure set version.

        Example:
            Please see above under the :meth:`proknow.Patients.StructureSetItem.draft` for example
            use.
        """
        if self._is_editable:
            wid = self._workspace_id
            sid = self._id
            lid = self._lock["id"]
            self._requestor.delete('/workspaces/' + wid + '/structuresets/' + sid + '/draft/lock/' + lid)
            self._lock = None
            self._is_editable = False

    def start_renewer(self):
        """Starts the lock renewer.

        Example:
            Please see above under the :meth:`proknow.Patients.StructureSetItem.draft` for example
            use.
        """
        if self._is_editable:
            self._renewer = StructureSetDraftLockRenewer(self)
            self._renewer.start()

    def stop_renewer(self):
        """Stops the lock renewer.

        Example:
            Please see above under the :meth:`proknow.Patients.StructureSetItem.draft` for example
            use.
        """
        if self._is_editable and self._renewer is not None:
            self._renewer.stop()
            self._renewer = None

class StructureSetRoiItem(object):
    """

    This class represents a stucture set ROI. It's instantiated by the
    :class:`proknow.Patients.StructureSetItem` class.

    Attributes:
        id (str): The id of the ROI (readonly).
        tag (str): The ROI tag (readonly).
        name (str): The name of the ROI.
        color (list): The color of the ROI represented as three numbers corresponding to the red,
            blue, and green components of the colors.
        type (str): The type of the ROI.

    """

    def __init__(self, structure_set, roi):
        """Initializes the StructureSetRoiItem class.

        Parameters:
            structure_set (:class:`proknow.Patients.StructureSetItem`): A structure set item.
            roi (dict): A dictionary attributes for the ROI.
        """
        self._structure_set = structure_set
        self._requestor = self._structure_set._requestor
        self._workspace_id = self._structure_set._workspace_id
        self._id = roi["id"]
        self._tag = roi["tag"]
        self._key = self._structure_set.data["key"]
        self.name = roi["name"]
        self.color = roi["color"]
        self.type = roi["type"]

    @property
    def id(self):
        return self._id

    @property
    def tag(self):
        return self._tag

    def delete(self):
        """Deletes the roi.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example deletes the ROI called BODY_2::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                for roi in structure_set.rois:
                    if roi.name == "BODY_2":
                        match = roi
                        break
                else:
                    match = None
                assert match is not None
                match.delete()
        """
        if not self._structure_set._is_editable:
            raise InvalidOperationError('Item is not editable')
        wid = self._workspace_id
        sid = self._structure_set._id
        rid = self._id
        headers = { 'ProKnow-Lock': self._structure_set._lock["id"] }
        self._requestor.delete('/workspaces/' + wid + '/structuresets/' + sid + '/draft/rois/' + rid, headers=headers)
        self._structure_set.rois.remove(self)

    def get_data(self):
        """Gets the data for an ROI (contours, lines, and points).

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Returns:
            :class:`proknow.Patients.StructureSetRoiData`: The ROI data representation.

        Example:
            This example dumps the contouring data for the structure PTV to file::

                from proknow import ProKnow
                import json

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                for roi in structure_set.rois:
                    if roi.name == "PTV":
                        match = roi
                        break
                else:
                    match = None
                assert match is not None
                data = match.get_data()
                with open('ptv_contours.json', 'w') as file:
                    json.dumps(data.contours, file)

        """
        headers = { 'ProKnow-Key': self._key }
        _, data = self._requestor.get('/structuresets/' + self._structure_set.id + '/rois/' + self._tag, headers=headers)
        return StructureSetRoiData(self, data)

    def is_editable(self):
        """Returns whether the ROI item is editable.

        Returns:
            bool: True if the ROI item is editable and False otherwise

        """
        return self._structure_set._is_editable

    def save(self):
        """Saves the roi.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example saves changes made to the name, color, and type of an ROI called BODY::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                for roi in structure_set.rois:
                    if roi.name == "BODY":
                        match = roi
                        break
                else:
                    match = None
                assert match is not None
                match.name = "PATIENT"
                match.color = [0, 238, 255]
                match.type = "EXTERNAL"
                match.save()
        """
        if not self._structure_set._is_editable:
            raise InvalidOperationError('Item is not editable')
        wid = self._workspace_id
        sid = self._structure_set._id
        rid = self._id
        headers = { 'ProKnow-Lock': self._structure_set._lock["id"] }
        body = {
            "name": self.name,
            "color": self.color,
            "type": self.type
        }
        self._requestor.put('/workspaces/' + wid + '/structuresets/' + sid + '/draft/rois/' + rid, body=body, headers=headers)

class StructureSetRoiData(object):
    """

    This class represents the data for a stucture set ROI. It's returned by calls to the
    :meth:`proknow.Patients.StructureSetRoiItem.get_data` method.

    Note:
        For information on how to use contour data, please check out the :ref:`contouring-data`
        guide.

    Attributes:
        contours (list): The list of contours for the ROI.
        lines (list): The list of lines for the ROI.
        points (list): The list of points for the ROI.

    """

    def __init__(self, roi_item, data):
        """Initializes the StructureSetRoiData class.

        Parameters:
            roi_item (:class:`proknow.Patients.StructureSetRoiItem`): A structure set ROI item.
            data (dict): A dictionary of the contouring, lines, and point data for the ROI.
        """
        self._roi_item = roi_item
        self._structure_set = roi_item._structure_set
        self._workspace_id = roi_item._structure_set._workspace_id
        self._requestor = roi_item._requestor
        self.contours = data["contours"]
        self.lines = data["lines"]
        self.points = data["points"]

    def is_editable(self):
        """Returns whether the ROI item is editable.

        Returns:
            bool: True if the ROI item is editable and False otherwise

        """
        return self._structure_set._is_editable

    def save(self):
        """Saves the roi data.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            This example clears the roi point data for a structure called PTV and saves the data::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                for roi in structure_set.rois:
                    if roi.name == "PTV":
                        match = roi
                        break
                else:
                    match = None
                assert match is not None
                data = match.get_data()
                data.points = []
                data.save()
        """
        if not self._structure_set._is_editable:
            raise InvalidOperationError('Item is not editable')
        wid = self._workspace_id
        sid = self._structure_set.id
        rid = self._roi_item.id
        body = {
            "version": 2,
            "contours": self.contours,
            "lines": self.lines,
            "points": self.points
        }
        headers = { 'ProKnow-Lock': self._structure_set._lock["id"] }
        _, result = self._requestor.put('/workspaces/' + wid + '/structuresets/' + sid + '/draft/rois/' + rid + '/data', body=body, headers=headers)
        self._roi_item._tag = result["tag"]
        print(rid, result["tag"])

class StructureSetVersions(object):
    """

    This class should be used to interact with the versions of a structure set. It is instantiated
    for you by the :class:`proknow.Patients.StructureSetItem` class.

    """

    def __init__(self, structure_set):
        """Initializes the StructureSetVersions class.

        Parameters:
            structure_set (proknow.Patients.StructureSetItem): The StructureSetItem instance that is
                instantiating the object.
        """
        self._structure_set = structure_set
        self._patients = structure_set._patients
        self._requestor = structure_set._requestor
        self._workspace_id = structure_set._workspace_id
        self._patient_id = structure_set._patient_id

    def delete(self, version_id):
        """Deletes a structure set version by id.

        Parameters:
            version_id (str): The id of the structure set version to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the version id, you can delete the version directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                entity.versions.delete('5c463a6c040040f1efda74db75c1b121')
        """
        assert isinstance(version_id, six.string_types), "`version_id` is required as a string."
        wid = self._workspace_id
        sid = self._structure_set._id
        self._requestor.delete('/workspaces/' + wid + '/structuresets/' + sid + '/versions/' + version_id)

    def get(self, version_id):
        """Gets a structure set item by id.

        Parameters:
            version_id (str): The id of the version to get or the string "draft".

        Returns:
            :class:`proknow.Patients.StructureSetItem`: A structure set item for the given version.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the version id, you can get the entity version directly using this
            method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                version = entity.versions.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(version_id, six.string_types), "`version_id` is required as a string."
        query = { 'version': version_id }
        wid = self._workspace_id
        pid = self._patient_id
        sid = self._structure_set._id
        _, structure_set = self._requestor.get('/workspaces/' + wid + '/structuresets/' + sid, query=query)
        return StructureSetItem(self._patients, wid, pid, structure_set, is_draft=(version_id=='draft'))

    def query(self):
        """Queries for structure set versions.

        Returns:
            list: A list of :class:`proknow.Patients.StructureSetVersionItem` objects.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the versions and prints the label and message of each version::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                for version in entity.versions.query():
                    print("label=" + version.label + "; message=" + message)
        """
        _, versions = self._requestor.get('/workspaces/' + self._workspace_id + '/structuresets/' + self._structure_set._id + '/versions')
        return [StructureSetVersionItem(self, self._workspace_id, self._structure_set._id, version) for version in versions]

class StructureSetVersionItem(object):
    """

    This class represents a version of a structure set. It is instantiated by the
    :meth:`proknow.Patients.StructureSetVersions.query` method.

    Attributes:
        id (str): The id of the structure set version item (readonly).
        data (dict): The complete representation of the version as returned from the API (readonly).
        status (str): The status of the version: either "archived" or "approved" (readonly).
        label (str): The structure set version label.
        message (str): The structure set version label.

    """

    def __init__(self, structure_set_versions, workspace_id, structure_set_id, version):
        self._structure_set_versions = structure_set_versions
        self._requestor = self._structure_set_versions._requestor
        self._structure_set = self._structure_set_versions._structure_set
        self._workspace_id = self._structure_set._workspace_id
        self._version_id = version["version"]
        self._status = version["status"]
        self._is_draft = version["status"] == "draft"
        self._data = version
        self.label = version["label"]
        self.message = version["message"]

    @property
    def data(self):
        return self._data

    @property
    def id(self):
        return self._version_id

    @property
    def status(self):
        return self._status

    def _wait(self):
        """Waits for the structure set to have the status of "ready" (before a download can begin).

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the version file to be generated.
        """
        start = datetime.utcnow()
        while True:
            wid = self._workspace_id
            sid = self._structure_set._id
            vid = self._version_id
            _, status = self._requestor.get('/workspaces/' + wid + '/structuresets/' + sid + '/versions/' + vid + '/status')
            if status["status"] == "ready":
                break
            elif (datetime.utcnow() - start).total_seconds() > 30: # pragma: no cover (difficult to test)
                raise TimeoutExceededError("Timeout of 30 seconds elapsed while waiting for structure set version")
            else:
                sleep(0.1) # 100 ms

    def delete(self):
        """Deletes the structure set version.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            The following example shows how to delete all archived versions of the structure set
            (i.e., all versions with a status of "archived" instead of "approved" and "draft")::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                archived = [version for version in entity.versions.query() if version.status == "archived"]
                for version in archived:
                    version.delete()
        """
        if self._is_draft:
            raise InvalidOperationError('Draft versions of structure sets cannot be deleted')
        self._structure_set_versions.delete(self._version_id)

    def download(self, path):
        """Download the version of the structure set.

        Parameters:
            path (str): A path to a directory or file to which the structure set file should be
            streamed.

        Returns:
            str: The absolute path to the downloaded file.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided path is invalid.
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the version file to be generated.

        Example:
            This example shows how to download the oldest structure set version for a patient as a
            file to the current directory::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                structure_set.versions.query()[-1].download("./")
        """
        if self._is_draft:
            raise InvalidOperationError('Draft versions of structure sets cannot be downloaded')

        assert isinstance(path, six.string_types), "`path` is required as a string."
        if os.path.isdir(path):
            resolved_path = os.path.join(os.path.abspath(path), "RS." + self._version_id + ".dcm")
        else:
            absolute = os.path.abspath(path)
            directory = os.path.dirname(path)
            if os.path.isdir(directory):
                resolved_path = absolute
            else:
                raise InvalidPathError('`' + path + '` is invalid')

        # Wait for version to be generated
        self._wait()

        # Download version
        wid = self._workspace_id
        sid = self._structure_set.id
        vid = self._version_id
        self._requestor.stream('/workspaces/' + wid + '/structuresets/' + sid + '/versions/' + vid + '/dicom', resolved_path)
        return resolved_path

    def get(self):
        """Gets a structure set item by id.

        Returns:
            :class:`proknow.Patients.StructureSetItem`: A structure set item corresponding to the
            version.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of StructureSetVersionItem objects into a
            list of StructureSetItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                structure_sets = [version.get() for version in entity.versions.query()]
        """
        if self._is_draft:
            return self._structure_set_versions.get("draft")
        else:
            return self._structure_set_versions.get(self._version_id)

    def revert(self):
        """Makes the version the approved version of the structure set.

        Returns:
            :class:`proknow.Patients.StructureSetItem`: A structure set item corresponding to the
            version.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            The following example shows how to make the original version of the structure set the
            approved version::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                original = entity.versions.query()[-1]
                original.revert()
        """
        if self._is_draft:
            raise InvalidOperationError('Draft versions of structure sets cannot be reverted')
        self._requestor.post('/workspaces/' + self._workspace_id + '/structuresets/' + self._structure_set._id + '/approve/' + self._version_id)
        return self._structure_set_versions.get("approved")

    def save(self):
        """Saves the changes made to the version.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If the operation cannot be performed.

        Example:
            The following example shows how to update the label and message for the original version
            of the structure set::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="structure_set")
                entity = entities[0].get()
                original = entity.versions.query()[-1]
                original.label = "original"
                original.message = "This is the original, imported version of the structure set."
                original.save()
        """
        if self._is_draft:
            raise InvalidOperationError('Draft versions of structure sets cannot be saved')
        body = {
            "label": self.label,
            "message": self.message
        }
        self._requestor.put('/workspaces/' + self._workspace_id + '/structuresets/' + self._structure_set._id + '/versions/' + self._version_id, body=body)
