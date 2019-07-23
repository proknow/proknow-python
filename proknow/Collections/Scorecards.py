import six


class CollectionScorecards(object):
    """

    This class should be used to interact with collection scorecards. It is instantiated for you as
    an attribute of the :class:`proknow.Collections.CollectionItem` class.

    """
    def __init__(self, collections, collection):
        """Initializes the CollectionScorecards class.

        Parameters:
            collections (proknow.Collections.Collections): The Collections instance that is
                instantiating the object.
            collection (proknow.Collections.CollectionItem): A instance of a CollectionItem.
        """
        self._collections = collections
        self._requestor = collections._requestor
        self._collection = collection

    def create(self, name, computed, custom):
        """Creates a new collection scorecard.

        Note:
            For information on how to construct computed metrics visit :ref:`computed-metrics`.

            For information on how to define scorecard objectives, see :ref:`scorecard-objectives`.

        Parameters:
            name (str): The scorecard name.
            computed (list): The computed metrics.
            custom (list): The custom metrics.

        Returns:
            :class:`proknow.Collections.CollectionScorecardItem`: A representation of the created
            collection scorecard

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new scorecard::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                collection.scorecards.create("My Scorecard", [{
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
        _, scorecard = self._requestor.post('/collections/' + self._collection.id + '/metrics/sets', json=body)
        return CollectionScorecardItem(self, self._collection, scorecard)

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
                collection = pk.collections.find(name='My Collection').get()
                collections.scorecards.delete('5c463a6c040040f1efda74db75c1b121')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        self._requestor.delete('/collections/' + self._collection.id + '/metrics/sets/' + scorecard_id)

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
            :class:`proknow.Collections.CollectionScorecardSummary`: A summary representation of the
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
            :class:`proknow.Collections.CollectionScorecardItem`: A complete representation of the
            collection scorecard

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the scorecard id, you can get the collection scorecard directly using this
            method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                scorecard = collection.scorecards.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        _, scorecard = self._requestor.get('/collections/' + self._collection.id + '/metrics/sets/' + scorecard_id)
        return CollectionScorecardItem(self, self._collection, scorecard)

    def query(self):
        """Queries for collection scorecards.

        Returns:
            list: A list of :class:`proknow.Collections.CollectionScorecardSummary` objects, each
            representing a summarized collection scorecard for the current collection.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the scorecards and prints the name of each scorecard::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                for scorecard in collection.scorecards.query():
                    print(scorecard.name)
        """
        _, scorecards = self._requestor.get('/collections/' + self._collection.id + '/metrics/sets')
        return [CollectionScorecardSummary(self, self._collection, scorecard) for scorecard in scorecards]

class CollectionScorecardSummary(object):
    """

    This class represents a summary view of a collection scorecard. It's instantiated by the
    :meth:`proknow.Collections.CollectionScorecards.query` method to represent each of the
    scorecards returned in a query result.

    Attributes:
        id (str): The id of the scorecard (readonly).
        name (str): The name of the scorecard (readonly).
        data (dict): The summary representation of the scorecard as returned from the API
            (readonly).

    """

    def __init__(self, scorecards, collection, scorecard):
        """Initializes the CollectionScorecardSummary class.

        Parameters:
            scorecards (proknow.Collections.CollectionScorecards): The CollectionScorecard instance
                that is instantiating the object.
            collection (proknow.Collections.CollectionItem): A instance of a CollectionItem.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecards = scorecards
        self._collection = collection
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
            :class:`proknow.Collections.CollectionScorecardItem`: A complete representation of the
            collection scorecard

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of CollectionScorecardSummary objects
            into a list of CollectionScorecardItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                collection = pk.collections.find(name='My Collection').get()
                scorecards = [scorecard.get() for scorecard in collection.scorecards.query()]
        """
        return self._scorecards.get(self._id)

class CollectionScorecardItem(object):
    """

    This class represents a collection scorecard. It's instantiated by the
    :class:`proknow.Collections.CollectionScorecards` class as a complete representation of the
    scorecard.

    Attributes:
        id (str): The id of the scorecard (readonly).
        data (dict): The complete representation of the scorecard as returned from the API
            (readonly).
        name (str): The name of the scorecard.
        computed (list): The computed metrics of the scorecard.
        custom (list): The custom metrics of the scorecard.

    """

    def __init__(self, scorecards, collection, scorecard):
        """Initializes the CollectionScorecardItem class.

        Parameters:
            scorecards (proknow.Collections.CollectionScorecards): The CollectionScorecard instance
                that is instantiating the object.
            collection (proknow.Collections.CollectionItem): A instance of a CollectionItem.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecards = scorecards
        self._requestor = self._scorecards._requestor
        self._collection = collection
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
                collection = pk.collections.find(name='My Collection').get()
                scorecard = collection.scorecards.find(name='My Scorecard').get()
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
                collection = pk.collections.find(name='My Collection').get()
                scorecard = collection.scorecards.find(name='My Scorecard').get()
                scorecard.custom = []
                scorecard.save()
        """
        body = {
            "name": self.name,
            "computed": self.computed,
            "custom": self.custom
        }
        _, scorecard = self._requestor.put('/collections/' + self._collection.id + '/metrics/sets/' + self._id, json=body)
        self._data = scorecard
        self.name = scorecard["name"]
        self.computed = scorecard["computed"]
        self.custom = scorecard["custom"]

