import six
import re

from .Exceptions import ScorecardTemplateLookupError


class ScorecardTemplates(object):
    """

    This class should be used to interact with scorecard templates.  It is instantiated for you as
    an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """
    def __init__(self, proknow, requestor):
        """Initializes the ScorecardTemplates class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor
        self._cache = None

    def create(self, name, computed, custom):
        """Creates a new scorecard template.

        Note:
            For information on how to construct computed metrics visit :ref:`computed-metrics`.

            For information on how to define scorecard objectives, see :ref:`scorecard-objectives`.

        Parameters:
            name (str): The scorecard name.
            computed (list): The computed metrics.
            custom (list): The custom metrics.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateItem`: A representation of the
            created scorecard template.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates a new scorecard template::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.scorecard_templates.create("My Scorecard", [{
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
        _, scorecard = self._requestor.post('/metrics/templates', json=body)
        self._cache = None
        return ScorecardTemplateItem(self, scorecard)

    def delete(self, scorecard_id):
        """Deletes a scorecard template by id.

        Parameters:
            scorecard_id (str): The id of the scorecard template to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the scorecard template id, you can delete the scorecard template directly
            using this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.scorecard_templates.delete('5c463a6c040040f1efda74db75c1b121')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        self._requestor.delete('/metrics/templates/' + scorecard_id)
        self._cache = None

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
            :class:`proknow.ScorecardTemplates.ScorecardTemplateSummary`: A summary representation
            of the matching scorecard.

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        if self._cache is None:
            self.query()
        if predicate is None and len(props) == 0:
            return None

        for scorecard in self._cache:
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
        """Gets a scorecard template by id.

        Parameters:
            scorecard_id (str): The id of the scorecard template to get.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateItem`: A complete representation of
            the scorecard template

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the scorecard template id, you can get the scorecard template directly using
            this method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.scorecard_templates.get('5c463a6c040068100c7f665acad17ac4')
        """
        assert isinstance(scorecard_id, six.string_types), "`scorecard_id` is required as a string."
        _, scorecard = self._requestor.get('/metrics/templates/' + scorecard_id)
        return ScorecardTemplateItem(self, scorecard)

    def resolve(self, scorecard_template):
        """Resolves a scorecard template by id or name.

        Parameters:
            scorecard_template (str): The scorecard template id or name.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateSummary`: A summary representation
            of the resolved scorecard.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.ScorecardTemplateLookupError`: If the scorecard template
                with the given id or name could not be found.
        """
        assert isinstance(scorecard_template, six.string_types), "`scorecard_template` is required as a string."

        pattern = re.compile(r"^[0-9a-f]{32}$")
        if pattern.match(scorecard_template) is not None:
            return self.resolve_by_id(scorecard_template)
        else:
            return self.resolve_by_name(scorecard_template)

    def resolve_by_name(self, name):
        """Resolves a scorecard template name to a scorecard template in a case insensitive manner.

        Parameters:
            name (str): The scorecard template name.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateSummary`: A summary representation
            of the resolved scorecard.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.ScorecardTemplateLookupError`: If the scorecard template
                with the given name could not be found.
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."

        if self._cache is None:
            self.query()
        normalized = name.lower()
        for item in self._cache:
            if item.name.lower() == normalized:
                scorecard_template = item
                break
        else:
            scorecard_template = None
        if scorecard_template is None:
            raise ScorecardTemplateLookupError("Scorecard template with name `" + name + "` not found.")
        return scorecard_template

    def resolve_by_id(self, scorecard_template_id):
        """Resolves a scorecard template id to a scorecard template.

        Parameters:
            scorecard_template_id (str): The scorecard template id.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateSummary`: A summary representation
            of the resolved scorecard.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.ScorecardTemplateLookupError`: If the scorecard template
                with the given id could not be found.
        """
        assert isinstance(scorecard_template_id, six.string_types), "`scorecard_template_id` is required as a string."

        scorecard_template = self.find(id=scorecard_template_id)
        if scorecard_template is None:
            raise ScorecardTemplateLookupError("Scorecard template with id `" + scorecard_template_id + "` not found.")
        return scorecard_template

    def query(self):
        """Queries for scorecards templates.

        Returns:
            list: A list of :class:`proknow.ScorecardTemplates.ScorecardTemplateSummary` objects,
            each representing a summarized scorecard template.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the scorecard templates and prints the name of each scorecard::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                for scorecard in pk.scorecard_templates.query():
                    print(scorecard.name)
        """
        _, scorecards = self._requestor.get('/metrics/templates')
        self._cache = [ScorecardTemplateSummary(self, scorecard) for scorecard in scorecards]
        return self._cache

class ScorecardTemplateSummary(object):
    """

    This class represents a summary view of a scorecard template. It's instantiated by the
    :meth:`proknow.ScorecardTemplates.ScorecardTemplates.query` method to represent each of the
    scorecards returned in a query result.

    Attributes:
        id (str): The id of the scorecard (readonly).
        name (str): The name of the scorecard (readonly).
        data (dict): The summary representation of the scorecard as returned from the API
            (readonly).

    """

    def __init__(self, scorecard_templates, scorecard):
        """Initializes the ScorecardTemplateSummary class.

        Parameters:
            scorecard_templates (proknow.ScorecardTemplates.ScorecardTemplates): The
                ScorecardTemplates instance that is instantiating the object.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecard_templates = scorecard_templates
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
        """Gets the complete representation of the scorecard template.

        Returns:
            :class:`proknow.ScorecardTemplates.ScorecardTemplateItem`: A complete representation of
            the scorecard template

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of ScorecardTemplateSummary objects into
            a list of ScorecardTemplateItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                scorecards = [scorecard.get() for scorecard in pk.scorecard_templates.query()]
        """
        return self._scorecard_templates.get(self._id)

class ScorecardTemplateItem(object):
    """

    This class represents a scorecard template. It's instantiated by the
    :class:`proknow.ScorecardTemplates.ScorecardTemplates` class as a complete representation of the
    scorecard.

    Attributes:
        id (str): The id of the scorecard (readonly).
        data (dict): The complete representation of the scorecard as returned from the API
            (readonly).
        name (str): The name of the scorecard.
        computed (list): The computed metrics of the scorecard.
        custom (list): The custom metrics of the scorecard.

    """

    def __init__(self, scorecard_templates, scorecard):
        """Initializes the ScorecardTemplateItem class.

        Parameters:
            scorecard_templates (proknow.ScorecardTemplates.ScorecardTemplates): The
                ScorecardTemplates instance that is instantiating the object.
            scorecard (dict): A dictionary of scorecard attributes.
        """
        self._scorecard_templates = scorecard_templates
        self._requestor = self._scorecard_templates._requestor
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
        """Deletes the scorecard template.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a scorecard template by its name and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                scorecard = pk.scorecard_templates.find(name='My Scorecard').get()
                scorecard.delete()
        """
        self._scorecard_templates.delete(self._id)

    def save(self):
        """Saves the changes made to a scorecard template.

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
                scorecard = pk.scorecard_templates.find(name='My Scorecard').get()
                scorecard.custom = []
                scorecard.save()
        """
        body = {
            "name": self.name,
            "computed": self.computed,
            "custom": self.custom
        }
        _, scorecard = self._requestor.put('/metrics/templates/' + self._id, json=body)
        self._data = scorecard
        self.name = scorecard["name"]
        self.computed = scorecard["computed"]
        self.custom = scorecard["custom"]
