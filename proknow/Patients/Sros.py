import os

from ..Exceptions import InvalidPathError


class SroSummary(object):
    """

    This class represents a summary view of a SRO. It's instantiated by the
    :meth:`proknow.Patients.StudySummary` class to represent each of the SROs that belong to the
    study.

    Attributes:
        id (str): The id of the SRO (readonly).
        data (dict): The summary representation of the SRO as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, sro):
        """Initializes the SroSummary class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the SRO belongs.
            sro (dict): A dictionary of sro attributes.
        """
        self._patients = patients
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = sro["id"]
        self._data = sro

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the SRO item for the SRO summary.

        Returns:
            :class:`proknow.Patients.SroItem` representing the SRO.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            Use this example to find all of the patient's SROs::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                sros = [sro.get() for sro in patient.find_sros(lambda sro: True)]
        """
        _, sro = self._requestor.get('/workspaces/' + self._workspace_id + '/sros/' + self._id)
        return SroItem(self._patients, self._workspace_id, self._patient_id, sro)

    def delete(self):
        """Deletes the SRO.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This examples shows how you can delete the SROs within a patient while leaving the
            patient intact::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                sros = patient.find_sros(lambda sro: True)
                for sro in sros:
                    sro.delete()
        """
        self._requestor.delete('/workspaces/' + self._workspace_id + '/sros/' + self._id)

class SroItem(object):
    """

    This class represents an SRO.

    Attributes:
        id (str): The id of the SRO (readonly).
        workspace_id (str): The id of the workspace (readonly).
        patient_id (str): The id of the patient (readonly).
        data (dict): The complete representation of the SRO as returned from the API (readonly).

    """

    def __init__(self, patients, workspace_id, patient_id, sro):
        """Initializes the SroItem class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the SRO belongs.
            sro (dict): A dictionary of SRO attributes.
        """
        self._patients = patients
        self._proknow = self._patients._proknow
        self._requestor = self._patients._requestor
        self._rtv = self._proknow.rtv
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = sro["id"]
        self._data = sro

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

    def delete(self):
        """Deletes the SRO.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This examples shows how you can delete the SROs within a patient while leaving the
            patient intact::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                sros = patient.find_sros(lambda sro: True)
                for sro in sros:
                    sro.get().delete()
        """
        self._requestor.delete('/workspaces/' + self._workspace_id + '/sros/' + self._id)

    def download(self, path):
        """Downloads the SRO file.

        Parameters:
            path (str): A path to a directory or file to which the SRO file should be streamed.

        Returns:
            str: The absolute path to the downloaded file.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidPathError`: If the provided path is invalid.

        Example:
            This example shows how to download an SRO file for a patient to the current directory::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                sros = patient.find_sros(name="reg")
                sro = sros[0].get()
                sro.download("./")
        """
        assert isinstance(path, str), "`path` is required as a string."
        if os.path.isdir(path):
            resolved_path = os.path.join(os.path.abspath(path), "REG." + self._data["uid"] + ".dcm")
        else:
            absolute = os.path.abspath(path)
            directory = os.path.dirname(path)
            if os.path.isdir(directory):
                resolved_path = absolute
            else:
                raise InvalidPathError('`' + path + '` is invalid')

        # TODO: This will be needed once it's possible to create/edit SROs
        # self._wait()

        self._requestor.stream('/workspaces/' + self._workspace_id + '/sros/' + self._id + '/dicom', resolved_path)
        return resolved_path
