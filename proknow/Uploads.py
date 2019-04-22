__all__ = [
    'Uploads',
]

import os
import six
import hashlib
from datetime import datetime
from requests_futures.sessions import FuturesSession

from .Exceptions import HttpError, InvalidPathError, TimeoutExceededError


class Uploads(object):
    """

    This class should be used to interact with the uploads in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the Uploads class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor

    def upload(self, workspace, path_or_paths):
        """Initiates an upload or series of uploads to the API.

        Parameters:
            workspace (str): An id or name of the workspace in which to create the uploads.
            path_or_paths (str or list): A path or list of paths such that each path is a directory
                of files to upload or a path to a file to upload.

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
            This example shows how to upload a directory of files::

                from proknow import ProKnow
                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.uploads.upload("Upload Test", "./DICOM")

            You may also provide the path to each file::

                from proknow import ProKnow
                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.uploads.upload("Upload Test", [
                    "./DICOM/img000001.dcm",
                    "./DICOM/img000002.dcm",
                    "./DICOM/img000003.dcm",
                    "./DICOM/img000004.dcm",
                    "./DICOM/img000005.dcm",
                ])

            Lists containing both directories and file paths are also permitted::

                from proknow import ProKnow
                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.uploads.upload("Upload Test", [
                    "./DICOM/CT/",
                    "./DICOM/structures.dcm",
                    "./DICOM/plan.dcm",
                    "./DICOM/dose.dcm",
                ])
        """
        if not isinstance(path_or_paths, list):
            path_or_paths = [path_or_paths]

        # Determine files to be added
        upload_file_paths = []
        for path in path_or_paths:
            assert isinstance(path, six.string_types), "provided path must be a string"
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for name in files:
                        upload_file_paths.append(os.path.abspath(os.path.join(root, name)))
            elif os.path.isfile(path):
                upload_file_paths.append(os.path.abspath(path))
            else:
                raise InvalidPathError("`" + path + "` is invalid.")

        # Resolve workspace
        workspace_id = self._proknow.workspaces.resolve(workspace).id

        # Construct requests session and get request information
        session = FuturesSession()
        auth = self._requestor.get_auth()
        base_url = self._requestor.get_base_url()

        # Create uploads from paths
        files = []
        for path in upload_file_paths:
            file = {}

            # Generate hash and determine file size
            md5 = hashlib.md5()
            with open(path, 'rb') as f:
                blocksize = 128 * md5.block_size
                for chunk in iter(lambda: f.read(blocksize), b''):
                    md5.update(chunk)
            checksum = md5.hexdigest()
            filesize = os.path.getsize(path)

            # Create upload
            _, upload = self._requestor.post('/workspaces/' + workspace_id + '/uploads', body={
                "checksum": checksum,
                "name": path,
                "size": filesize,
                "multipart": False,
            })
            file["path"] = path
            file["upload"] = upload

            # Upload chunk
            file["chunk_request"] = session.post(base_url + '/uploads/chunks', auth=auth, headers={
                "ProKnow-Key": upload['key'],
            }, data={
                "flowChunkNumber": 1,
                "flowChunkSize": filesize,
                "flowCurrentChunkSize": filesize,
                "flowTotalChunks": 1,
                "flowTotalSize": filesize,
                "flowIdentifier": upload["identifier"],
                "flowFilename": path,
                "flowMultipart": False,
            }, files={
                "file": open(path, 'rb'),
            })

            files.append(file)

        # Wait for uploads to complete and construct lookup dictionary
        for file in files:
            result = file["chunk_request"].result()
            if result.status_code >= 400: # pragma: no cover (difficult to test)
                raise HttpError(result.status_code, result.text)

        # Wait for uploads to come to terminal state
        query = None
        last_change = datetime.utcnow()
        while True:
            terminal_count = 0
            _, uploads = self._requestor.get('/workspaces/' + workspace_id + '/uploads', query=query)

            done = True
            for file in files:
                # Skip file if already resolved
                try:
                    if file["upload_result"]["status"] in ("completed", "pending", "failed"):
                        continue
                    else: # pragma: no cover (cannot hit)
                        pass
                except KeyError:
                    pass

                # Attempt to find 
                upload_id = file["upload"]["id"]
                upload_match = None
                for upload in uploads:
                    if upload["id"] == upload_id:
                        upload_match = upload
                        break
                if upload_match is not None:
                    if upload_match["status"] in ("completed", "pending", "failed"):
                        file["upload_result"] = upload_match
                        terminal_count += 1
                        continue

                # Matching upload was not found or status was not terminal
                done = False

            if terminal_count > 0:
                last_change = datetime.utcnow()

            if done:
                break
            elif (datetime.utcnow() - last_change).total_seconds() > 30: # pragma: no cover (difficult to test)
                raise TimeoutExceededError("Timeout of 30 seconds elapsed while waiting for uploads to finish")
            elif len(uploads) > 0:
                last_upload = uploads[-1]
                query = {
                    "updated": last_upload["updated_at"],
                    "after": last_upload["id"],
                }

        # Construct Upload Batch
        return UploadBatch(self, workspace_id, [{
            "path": file["path"],
            "upload": file["upload_result"],
        } for file in files])

class UploadBatch(object):
    """

    This class is instantiated by the :meth:`proknow.Uploads.Uploads.upload` method and is used as
    an interface for looking up patients and entities within a batch of resolved uploads.

    Attributes
        patients (list): A list of :class:`proknow.Patients.UploadPatientSummary` items.

    """

    def __init__(self, uploads, workspace_id, files):
        """Initializes the UploadBatch class.

        Parameters:
            uploads (proknow.Uploads.Uploads): The Uploads instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the uploads belong.
            files (list): A list of files.
        """
        self._uploads = uploads
        self._workspace_id = workspace_id
        self._file_lookup = {}
        self._patient_lookup = {}
        self._entity_lookup = {}
        self._patients = []

        for file in files:
            path = file["path"]
            upload = file["upload"]
            self._file_lookup[path] = upload

            if upload["status"] == "completed":
                patient_id = upload["patient"]["id"]
                entity_id = upload["entity"]["id"]
                try:
                    patient = self._patient_lookup[patient_id]
                except KeyError:
                    patient = UploadPatientSummary(self._uploads, self._workspace_id, upload["patient"])
                    self._patient_lookup[patient_id] = patient;
                    self._patients.append(patient)
                try:
                    entity = self._entity_lookup[entity_id]
                except KeyError:
                    entity = UploadEntitySummary(self._uploads, self._workspace_id, patient_id, upload["entity"])
                    self._entity_lookup[entity_id] = entity
                    patient.add_entity(entity)
            else: # pragma: no cover (cannot hit)
                pass

    @property
    def patients(self):
        return self._patients

    def find_patient(self, path):
        """Find the patient associated with the given file.

        Parameters:
            path (str): An absolute file path.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided file path is invalid.

        Example:
            This example shows how to find a patient associated with a given file upload::

                from proknow import ProKnow
                import os

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                batch = pk.uploads.upload("Upload Test", "./DICOM")
                path = os.path.abspath("./DICOM/plan.dcm")
                patient_summary = batch.find_patient(path)
        """
        assert isinstance(path, six.string_types), "`path` is required as a string."

        try:
            upload = self._file_lookup[path]
        except:
            raise InvalidPathError('`' + path + '` not found in current batch')

        assert upload["status"] == "completed", "Upload is not complete"
        patient_id = upload["patient"]["id"]

        return self._patient_lookup[patient_id]

    def find_entity(self, path):
        """Find the entity associated with the given file.

        Parameters:
            path (str): An absolute file path.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided file path is invalid.

        Example:
            This example shows how to find an entity associated with a given file upload::

                from proknow import ProKnow
                import os

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                batch = pk.uploads.upload("Upload Test", "./DICOM")
                path = os.path.abspath("./DICOM/plan.dcm")
                entity_summary = batch.find_entity(path)
        """
        assert isinstance(path, six.string_types), "`path` is required as a string."

        try:
            upload = self._file_lookup[path]
        except:
            raise InvalidPathError('`' + path + '` not found in current batch')

        assert upload["status"] == "completed", "Upload is not complete"
        entity_id = upload["entity"]["id"]

        return self._entity_lookup[entity_id]

class UploadPatientSummary(object):
    """

    This class provides a summary view of a patient as returned as part of an upload.

    Attributes:
        id (str): The id of the patient (readonly).
        data (dict): The summary representation of the patient as returned from the API for an
            upload (readonly).
        entities (list): A list of :class:`proknow.Uploads.UploadEntitySummary` items.

    """

    def __init__(self, uploads, workspace_id, patient):
        """Initializes the UploadPatientSummary class.

        Parameters:
            uploads (proknow.Uploads.Uploads): The Uploads instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient (dict): Patient summary information.
        """
        self._uploads = uploads
        self._proknow = uploads._proknow
        self._workspace_id = workspace_id
        self._id = patient["id"]
        self._data = patient
        self._entities = []

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def entities(self):
        return self._entities

    def add_entity(self, entity):
        """Adds an entity to patient summary.

        Parameters:
            entity (:class:`proknow.Uploads.UploadEntitySummary`): An entity summary to add to the
                patient summary.
        """
        self._entities.append(entity)

    def get(self):
        """Gets the complete representation of the patient.

        Returns:
            :class:`proknow.Patients.PatientItem`: an object representing a patient in the
            organization.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to get a list of patient items associated with a batch of
            uploads::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                batch = pk.uploads.upload("Upload Test", "./DICOM")
                patients = [patient.get() for patient in batch.patients]
        """
        return self._proknow.patients.get(self._workspace_id, self._id)

class UploadEntitySummary(object):
    """

    This class provides a summary view of a entity as returned as part of an upload.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API for an
            upload (readonly).

    """

    def __init__(self, uploads, workspace_id, patient_id, entity):
        """Initializes the UploadEntitySummary class.

        Parameters:
            uploads (proknow.Uploads.Uploads): The Uploads instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the entity belongs.
            patient_id (str): The id of the patient to which the entity belongs
            entity (dict): entity summary information.
        """
        self._uploads = uploads
        self._proknow = uploads._proknow
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

    def get(self):
        """Gets the complete representation of the entity.

        Returns:
            One of (:class:`proknow.Patients.ImageSetItem`,
            :class:`proknow.Patients.StructureSetItem`, :class:`proknow.Patients.PlanItem`,
            :class:`proknow.Patients.DoseItem`) based on the entity summary type.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to get a list of entity items associated with a batch of
            uploads::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                batch = pk.uploads.upload("Upload Test", "./DICOM")
                entities = [entity.get() for patient in batch.patients for entity in patient.entities]
        """
        patient = self._proknow.patients.get(self._workspace_id, self._patient_id)
        entity = patient.find_entities(id=self._id)[0]
        return entity.get()
