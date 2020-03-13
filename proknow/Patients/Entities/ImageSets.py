import os
import six

from .EntityItem import EntityItem
from ...Exceptions import InvalidPathError


class ImageSetItem(EntityItem):
    """

    This class represents a an image set. It's instantiated by the
    :class:`proknow.Patients.EntitySummary` class as a complete representation of an image set
    entity.

    Attributes:
        id (str): The id of the entity (readonly).
        data (dict): The complete representation of the entity as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, entity):
        """Initializes the ImageSetItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the entity belongs.
            entity (dict): A dictionary of entity attributes.
        """
        super(ImageSetItem, self).__init__(patients, workspace_id, patient_id, entity)

    def download(self, path):
        """Download the image set as a directory of images.

        Parameters:
            path (str): A path to a directory in which a directory of images should be downloaded.

        Returns:
            str: The absolute path to the downloaded image set directory.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided path is invalid.

        Example:
            This example shows how to download an image set into the current directory::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="image_set")
                image_set = entities[0].get()
                image_set.download("./")
        """
        assert isinstance(path, six.string_types), "`path` is required as a string."
        modality = self._data["modality"]
        if os.path.isdir(path):
            main_directory = os.path.join(os.path.abspath(path), modality + "." + self._data["uid"])
        else:
            raise InvalidPathError('`' + path + '` is invalid')
        os.mkdir(main_directory)

        for image in self._data["data"]["images"]:
            image_path = os.path.join(main_directory, modality + "." + image["uid"])
            self._requestor.stream('/workspaces/' + self._workspace_id + '/imagesets/' + self._id + '/images/' + image["id"] + '/dicom', image_path)
        return main_directory

    def get_image_data(self, index):
        """Gets the image data for the image at the given index.

        Parameters:
            index (int): The index of the image for which to get the data.

        Returns:
            bytes: The image data.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to get the image data for each image in an image set::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="image_set")
                image_set = entities[0].get()
                slice_count = len(image_set.data["data"]["images"])
                slice_data = [image_set.get_image_data(i) for i in range(slice_count)]
        """
        assert isinstance(index, int), "`index` is required as an integer."
        image = self.data["data"]["images"][index]
        headers = {
            'ProKnow-Key': self.data["key"]
        }
        _, content = self._requestor.get_binary('/imagesets/' + self._id + '/images/' + image["tag"], headers=headers)
        return content

    def refresh(self):
        """Refreshes the image set entity.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example shows how to refresh an image set entity::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                entities = patient.find_entities(type="image_set")
                image_set = entities[0].get()
                image_set.refresh()
        """
        _, image_set = self._requestor.get('/workspaces/' + self._workspace_id + '/imagesets/' + self._id)
        self._update(image_set)
