import os
import six

from .EntityItem import EntityItem
from ...Exceptions import InvalidPathError


class StructureSetItem(EntityItem):
    """

    This class represents a structure set. It's instantiated by the
    :class:`proknow.Patients.EntitySummary` class as a complete representation of a structure set
    entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The summary representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the StructureSetItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        super(StructureSetItem, self).__init__(patients, workspace_id, patient_id, entity)
        self.rois = [StructureSetRoiItem(self, roi) for roi in entity["data"]["rois"]]

    def download(self, path):
        """Download the currently approved structure set file.

        Parameters:
            path (str): A path to a directory or file to which the structure set file should be
            streamed.

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
                entities = patient.find_entities(type="structure_set")
                structure_set = entities[0].get()
                structure_set.download("./")
        """
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
        self._requestor.stream('/workspaces/' + self._workspace_id + '/structuresets/' + self._id + '/versions/' + self._data["data"]["version"] + '/dicom', resolved_path)
        return resolved_path

class StructureSetRoiItem(object):
    """

    This class represents a stucture set ROI. It's instantiated by the
    :class:`proknow.Patients.StructureSetItem` class.

    Attributes:
        name (str): The name of the ROI (readonly).
        color (list): The color of the ROI represented as three numbers corresponding to the red,
            blue, and green components of the colors (readonly).
        type (str): The type of the ROI (readonly).

    """

    def __init__(self, structure_set, roi):
        """Initializes the StructureSetRoiItem class.

        Parameters:
            structure_set (:class:`proknow.Patients.StructureSetItem`): A structure set item.
            roi (dict): A dictionary attributes for the ROI.
        """
        self._structure_set = structure_set
        self._requestor = self._structure_set._requestor
        self._roi = roi
        self._tag = roi["tag"]
        self._key = self._structure_set.data["key"]
        self._name = roi["name"]
        self._color = roi["color"]
        self._type = roi["type"]

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def type(self):
        return self._type

    def get_data(self):
        """

        Gets the data for an ROI (contours, lines, and points).

        Returns:
            :class:`proknow.Patients.StructureSetRoiData`: The ROI data representation.

        """
        headers = { 'ProKnow-Key': self._key }
        _, data = self._requestor.get('/structuresets/' + self._structure_set.id + '/rois/' + self._tag, headers=headers)
        return StructureSetRoiData(data)

class StructureSetRoiData(object):
    """

    This class represents the data for a stucture set ROI. It's returned by calls to the
    :meth:`proknow.Patients.StructureSetRoiItem.get_data` method.

    Attributes:
        contours (list): The list of contours for the ROI (readonly).
        lines (list): The list of lines for the ROI (readonly).
        points (list): The list of points for the ROI (readonly).

    """

    def __init__(self, data):
        """Initializes the StructureSetRoiData class.

        Parameters:
            data (dict): A dictionary of the contouring, lines, and point data for the ROI.
        """
        self._contours = data["contours"]
        self._lines = data["lines"]
        self._points = data["points"]
