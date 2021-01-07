import six


class PatientScorecards(object):
    """

    This class should be used to interact with patient scorecards. It is instantiated for you as an
    attribute of the :class:`proknow.Patients.PatientItem` class.

    """
    def __init__(self, patients, workspace_id, patient_id):
        """Initializes the PatientScorecards class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient.
        """
        self._patients = patients
        self._requestor = patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id

    def create(self, name, computed, custom):
        """Creates a new patient scorecard.

        Note:
            For information on how to construct computed metrics visit :ref:`computed-metrics`.

            For information on how to define scorecard objectives, see :ref:`scorecard-objectives`.

        Parameters:
            name (str): The scorecard name.
            computed (list): The computed metrics.
            custom (list): The custom metrics.

        Returns:
            :class:`proknow.Patients.PatientScorecardItem`: A representation of the created patient
            scorecard

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new scorecard::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                patient.scorecards.create("My Scorecard", [{
                    "type": "VOLUME",
                    "roi_name": "BRAINSTEM",
                    "arg_1": None,
                    "arg_2": None
                }, {
                    "type": "VOLUME_CC_DOSE_RANGE_ROI",
                    "roi_name": "BRAINSTEM",
                    "arg_1": 30,
                    "arg_2": 60,
                    "objectives": [{
                        "label": "IDEAL",
                        "color": [18, 191, 0],
                        "max": 0
                    }, {
                        "label": "GOOD",
                        "color": [136, 223, 127],
                        "max": 3
                    }, {
                        "label": "ACCEPTABLE",
                        "color": [255, 216, 0],
                        "max": 6
                    }, {
                        "label": "MARGINAL",
                        "color": [255, 102, 0],
                        "max": 9
                    }, {
                        "label": "UNACCEPTABLE",
                        "color": [255, 0, 0]
                    }]
                }], [{
                    "id": pk.custom_metrics.resolve_by_name("Genetic Type").id
                }])
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(computed, list), "`computed` is required as a list."
        assert isinstance(custom, list), "`custom` is required as a list."

        body = {'name': name, 'computed': computed, 'custom': custom}
        _, scorecard = self._requestor.post('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/metrics/sets', json=body)
        return PatientScorecardItem(self, self._workspace_id, self._patient_id, scorecard)

    def delete(self, scorecard_id):
        """Deletes a scorecard by id.

        Parameters:
            scorecard_id (str): The id of the scorecard to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the scorecard id, you can delete the scorecard directly using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                patient.scorecards.delete('5c463a6c040040f1efda74db75c1b121')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        self._requestor.delete('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/metrics/sets/' + scorecard_id)

    def find(self, predicate=None, **props):
        """Finds the first scorecard that matches the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Parameters:
            predicate (func): A function that is passed a scorecard as input and which should return
                a bool indicating whether the scorecard is a match.
            **props: A dictionary of keyword arguments that may include any scorecard attribute.
                These arguments are considered in turn to find matching scorecards.

        Returns:
            :class:`proknow.Patients.PatientScorecardSummary`: A summary representation of the
            matching scorecard.

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        if predicate is None and len(props) == 0:
            return None

        scorecards = self.query()
        for scorecard in scorecards:
            match = True
            if predicate is not None and not predicate(scorecard):
                match = False
            for key in props:
                if scorecard._data[key] != props[key]:
                    match = False
            if match:
                return scorecard

        return None

    def get(self, scorecard_id):
        """Gets a scorecard by id.

        Parameters:
            scorecard_id (str): The id of the scorecard to get.

        Returns:
            :class:`proknow.Patients.PatientScorecardItem`: A complete representation of the patient
            scorecard

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the scorecard id, you can get the patient scorecard directly using this
            method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                scorecard = patient.scorecards.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        _, scorecard = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/metrics/sets/' + scorecard_id)
        return PatientScorecardItem(self, self._workspace_id, self._patient_id, scorecard)

    def query(self):
        """Queries for patient scorecards.

        Returns:
            list: A list of :class:`proknow.Patients.PatientScorecardSummary` objects, each
            representing a summarized patient scorecard for the current patient.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the scorecards and prints the name of each scorecard::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                for scorecard in patient.scorecards.query():
                    print(scorecard.name)
        """
        _, scorecards = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/metrics/sets')
        return [PatientScorecardSummary(self, self._workspace_id, self._patient_id, scorecard) for scorecard in scorecards]

class PatientScorecardSummary(object):
    """

    This class represents a summary view of a patient scorecard. It's instantiated by the
    :meth:`proknow.Patients.PatientScorecards.query` method to represent each of the scorecards
    returned in a query result.

    Attributes:
        id (str): The id of the scorecard (readonly).
        name (str): The name of the scorecard (readonly).
        data (dict): The summary representation of the scorecard as returned from the API
            (readonly).

    """

    def __init__(self, scorecards, workspace_id, patient_id, scorecard):
        """Initializes the PatientScorecardSummary class.

        Parameters:
            scorecards (proknow.Patients.PatientScorecards): The PatientScorecard instance that is
                instantiating the object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecards = scorecards
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._data = scorecard
        self._id = scorecard["id"]
        self._name = scorecard["name"]

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the scorecard.

        Returns:
            :class:`proknow.Patients.PatientScorecardItem`: A complete representation of the patient
            scorecard

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of PatientScorecardSummary objects into a
            list of PatientScorecardItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                scorecards = [scorecard.get() for scorecard in patient.scorecards.query()]
        """
        return self._scorecards.get(self._id)

class PatientScorecardItem(object):
    """

    This class represents a patient scorecard. It's instantiated by the
    :class:`proknow.Patients.PatientScorecards` class as a complete representation of the
    scorecard.

    Attributes:
        id (str): The id of the scorecard (readonly).
        data (dict): The complete representation of the scorecard as returned from the API
            (readonly).
        name (str): The name of the scorecard.
        computed (list): The computed metrics of the scorecard.
        custom (list): The custom metrics of the scorecard.

    """

    def __init__(self, scorecards, workspace_id, patient_id, scorecard):
        """Initializes the PatientScorecardItem class.

        Parameters:
            scorecards (proknow.Patients.PatientScorecards): The PatientScorecard instance that is
                instantiating the object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecards = scorecards
        self._requestor = self._scorecards._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._data = scorecard
        self._id = scorecard["id"]
        self.name = scorecard["name"]
        self.computed = scorecard["computed"]
        self.custom = scorecard["custom"]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the scorecard.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a scorecard by its name and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                scorecard = patient.scorecards.find(name='My Scorecard').get()
                scorecard.delete()
        """
        self._scorecards.delete(self._id)

    def save(self):
        """Saves the changes made to a scorecard.

        Note:
            For information on how to construct computed metrics visit :ref:`computed-metrics`.

            For information on how to define scorecard objectives, see :ref:`scorecard-objectives`.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a scorecard by its name, remove the associated
            custom metrics, and save it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
                patient = patients[0].get()
                scorecard = patient.scorecards.find(name='My Scorecard').get()
                scorecard.custom = []
                scorecard.save()
        """
        body = {
            "name": self.name,
            "computed": self.computed,
            "custom": self.custom
        }
        _, scorecard = self._requestor.put('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/metrics/sets/' + self._id, json=body)
        self._data = scorecard
        self.name = scorecard["name"]
        self.computed = scorecard["computed"]
        self.custom = scorecard["custom"]
