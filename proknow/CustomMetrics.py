__all__ = [
    'CustomMetrics',
]

import six
import re

from .Exceptions import CustomMetricLookupError


class CustomMetrics(object):
    """

    This class should be used to interact with the custom metrics in a ProKnow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.

    """

    def __init__(self, proknow, requestor):
        """Initializes the CustomMetrics class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor
        self._cache = None

    def create(self, name, context, type):
        """Creates a new custom metric.

        Parameters:
            name (str): The custom metric name.
            context (str): The custom metric context.
            type (dict): The custom metric type.

        Returns:
            :class:`proknow.CustomMetrics.CustomMetricItem`: A representation of the created custom
            metric.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example creates three new custom metrics, demonstrating each of the available
            custom metric types::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.custom_metrics.create('Genetic Type', "patient", {
                    "enum": {
                        "values": ["Type I", "Type II", "Type III", "Type IV"]
                    }
                })
                pk.custom_metrics.create('Physician Name', "patient", {
                    "string": {}
                })
                pk.custom_metrics.create('Toxicity of Larynx (1-4)', "patient", {
                    "number": {}
                })
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."
        assert isinstance(context, six.string_types), "`context` is required as a string."
        assert isinstance(type, dict), "`type` is required as a dict."

        _, custom_metric = self._requestor.post('/metrics/custom', body={'name': name, 'context': context, 'type': type})
        self._cache = None
        return CustomMetricItem(self, custom_metric)

    def delete(self, custom_metric_id):
        """Deletes a custom metric by id.

        Parameters:
            custom_metric_id (str): The id of the custom metric to delete.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            If you know the custom metric id, you can delete the custom metric directly using this
            method::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                pk.custom_metrics.delete('5c463a6c040040f1efda74db75c1b121')
        """
        assert isinstance(custom_metric_id, six.string_types), "`custom_metric_id` is required as a string."
        self._requestor.delete('/metrics/custom/' + custom_metric_id)
        self._cache = None

    def find(self, predicate=None, **props):
        """Finds the first custom metric that matches the input paramters.

        Note:
            For more information on how to use this method, see :ref:`find-methods`.

        Note:
            This method utilizes a cache of custom metrics. Once it has a cache of custom metrics,
            it will use that cache until the :meth:`proknow.CustomMetrics.CustomMetrics.query`
            method is called to refresh the cache. If you wish to make your code resilient to
            custom metric changes (i.e., new custom metrics, renamed custom metrics, deleted custom
            metrics, etc.) while your script is running, you should call the
            :meth:`proknow.CustomMetrics.CustomMetrics.query` method before this method. In most
            use cases, this is not necessary.

        Parameters:
            predicate (func): A function that is passed a metric as input and which should return
                a bool indicating whether the metric is a match.
            **props: A dictionary of keyword arguments that may include any custom metric attribute.
                These arguments are considered in turn to find matching custom metrics.

        Returns:
            :class:`proknow.CustomMetrics.CustomMetricItem`: A representation of the matching
            custom metric.

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        if self._cache is None:
            self.query()
        if predicate is None and len(props) == 0:
            return None

        for metric in self._cache:
            match = True
            if predicate is not None and not predicate(metric):
                match = False
            for key in props:
                if metric._data[key] != props[key]:
                    match = False
            if match:
                return metric

        return None

    def resolve(self, custom_metric):
        """Resolves a metric by id or name.

        Parameters:
            custom_metric (str): The metric id or name.

        Returns:
            :class:`proknow.CustomMetrics.CustomMetricItem`: A representation of the resolved
            custom metric.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.CustomMetricLookupError`: If the custom metric with the
                given id or name could not be found.
        """
        assert isinstance(custom_metric, six.string_types), "`custom_metric` is required as a string."

        pattern = re.compile(r"^[0-9a-f]{32}$")
        if pattern.match(custom_metric) is not None:
            return self.resolve_by_id(custom_metric)
        else:
            return self.resolve_by_name(custom_metric)

    def resolve_by_name(self, name):
        """Resolves a custom metric name to a custom metric.

        Parameters:
            name (str): The custom metric name.

        Returns:
            :class:`proknow.CustomMetrics.CustomMetricItem`: A representation of the resolved
            custom metric.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.CustomMetricLookupError`: If the custom metric with the given
                name could not be found.
        """
        assert isinstance(name, six.string_types), "`name` is required as a string."

        custom_metric = self.find(name=name)
        if custom_metric is None:
            raise CustomMetricLookupError("Custom metric with name `" + name + "` not found.")
        return custom_metric

    def resolve_by_id(self, custom_metric_id):
        """Resolves a custom metric id to a custom metric.

        Parameters:
            custom_metric_id (str): The custom metric id.

        Returns:
            :class:`proknow.CustomMetrics.CustomMetricItem`: A representation of the resolved
            custom metric.

        Raises:
            AssertionError: If the input parameters are invalid.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.CustomMetricLookupError`: If the custom metric with the given
                id could not be found.
        """
        assert isinstance(custom_metric_id, six.string_types), "`custom_metric_id` is required as a string."

        custom_metric = self.find(id=custom_metric_id)
        if custom_metric is None:
            raise CustomMetricLookupError("Custom metric with id `" + custom_metric_id + "` not found.")
        return custom_metric

    def query(self):
        """Queries for custom metrics.

        Note:
            This method refreshes the custom metric cache.

        Returns:
            list: A list of :class:`proknow.CustomMetrics.CustomMetricItem` objects, each
            representing a custom metric in the organization.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            This example queries the custom metrics and prints the name of each custom metric::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                for custom_metric in pk.custom_metrics.query():
                    print(custom_metric.name)
        """
        _, custom_metrics = self._requestor.get('/metrics/custom')
        self._cache = [CustomMetricItem(self, custom_metric) for custom_metric in custom_metrics]
        return self._cache

class CustomMetricItem(object):
    """

    This class represents a custom metric. It's instantiated by the
    :class:`proknow.CustomMetrics.CustomMetrics` class to represent each of the custom metrics in a
    query result and a created custom metric.

    Attributes:
        id (str): The id of the custom metric (readonly).
        data (dict): The complete representation of the custom metric as returned from the API
            (readonly).
        name (str): The name of the custom metric.
        context (str): The context of the custom metric.
        type (dict): The type of the custom metric (readonly).

    """

    def __init__(self, custom_metrics, custom_metric):
        """Initializes the CustomMetricItem class.

        Parameters:
            custom_metrics (proknow.CustomMetrics.CustomMetrics): The CustomMetrics instance that is
                instantiating the object.
            custom_metric (dict): A dictionary of custom metric attributes.
        """
        self._custom_metrics = custom_metrics
        self._requestor = self._custom_metrics._requestor
        self._id = custom_metric["id"]
        self._data = custom_metric
        self.name = custom_metric["name"]
        self.context = custom_metric["context"]
        self._type = custom_metric["type"]

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def type(self):
        # TODO: This will become read-write once the type can be edited.
        return self._type

    def delete(self):
        """Deletes the custom metric.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a custom metric by its name and delete it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                metric = pk.custom_metric.find(name='Type')
                metric.name = "Genetic Type"
                metric.save()
        """
        self._custom_metrics.delete(self._id)

    def save(self):
        """Saves the changes made to a custom metric.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to find a custom metric by its name, change the
            name, and save it::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                metric = pk.custom_metric.find(name='Type')
                metric.name = "Genetic Type"
                metric.save()
        """
        _, custom_metric = self._requestor.put('/metrics/custom/' + self._id, body={'name': self.name, 'context': self.context})
        self._data = custom_metric
        self.name = custom_metric["name"]
        self.context = custom_metric["context"]
        self._type = custom_metric["type"]
