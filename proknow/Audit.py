__all__ = [
    'Audit',
]

import json
import datetime

from proknow.Exceptions import InvalidOperationError

class Audit(object):
    """
    This class should be used to interact with the audit logs in a Proknow organization.
    """

    def __init__(self, proknow, requestor):
        """Initializes the Audit class.

        Parameters:
            proknow (proknow.ProKnow.ProKnow): The ProKnow instance that is instantiating the
                object.
            requestor (proknow.Requestor.Requestor): An object used to make API requests.
        """
        self._proknow = proknow
        self._requestor = requestor
        self.auditResultsPage = None
    
    def query(self, page_size=25, **kwargs):

        """Queries for audit logs.

        Parameters:
            page_size (int, optional): (Default is 25) The number of items for each page
            start_time (datetime): Start time cut off for whole query
            end_time (datetime): End time cut off for whole query
            types (str or list): List of event types
            user_id (str): ID of events' enacting user
            user_name (str): Name of events' enacting user
            patient_id (str): ID of patient
            patient_name (str): Name of patient
            patient_mrn (str): Medical record number of patient
            workspace_id (str): ID of workspace in which events took place
            workspace_name (str): Name of workspace in which events took place
            collection_id (str): ID of a collection
            resource_id (str): ID of a resource
            resource_name (str): Name of a resource
            classification (str): 'HTTP' or 'AUTH'
            methods (str or list): List of HTTP methods: 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', or 'PATCH'
            uri (str): Filter by the uri that events took place (e.g. '/metrics/custom')
            user_agent (str): User Agent attributed to events (e.g. Browser User Agent)
            ip_address (str): IP Address attributed to events
            status_codes (str or list): List of status codes of events (e.g. 200)
            text (str or list): Text to search for in all text fields

        Returns:
            A :class:`proknow.Audit.AuditResultsPage` object, representing a page of query results

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """

        self.options = {}
        if page_size is not None: self.options["page_size"] = page_size
        if "start_time" in kwargs : self.options["start_time"] = kwargs["start_time"].isoformat()
        if "end_time" in kwargs: self.options["end_time"] = kwargs["end_time"].isoformat()
        if "user_id" in kwargs: self.options["user_id"] = kwargs["user_id"] 
        if "user_name" in kwargs: self.options["user_name"] = kwargs["user_name"]
        if "patient_id" in kwargs: self.options["patient_id"] = kwargs["patient_id"]
        if "patient_name" in kwargs: self.options["patient_name"] = kwargs["patient_name"]
        if "patient_mrn" in kwargs: self.options["patient_mrn"] = kwargs["patient_mrn"]
        if "workspace_id" in kwargs: self.options["workspace_id"] = kwargs["workspace_id"]
        if "workspace_name" in kwargs: self.options["workspace_name"] = kwargs["workspace_name"]
        if "collection_id" in kwargs: self.options["collection_id"] = kwargs["collection_id"]
        if "resource_id" in kwargs: self.options["resource_id"] = kwargs["resource_id"]
        if "resource_name" in kwargs: self.options["resource_name"] = kwargs["resource_name"] 
        if "classification" in kwargs: self.options["classification"] = kwargs["classification"].upper() 
        if "uri" in kwargs: self.options["uri"] = kwargs["uri"] 
        if "user_agent" in kwargs: self.options["user_agent"] = kwargs["user_agent"]
        if "ip_address" in kwargs: self.options["ip_address"] = kwargs["ip_address"]

        if "types" in kwargs: 
            if not isinstance(kwargs["types"], list):
                self.options["types"] = [kwargs["types"]]
            else:
                self.options["types"] = kwargs["types"]

        if "methods" in kwargs: 
            if not isinstance(kwargs["methods"], list):
                self.options["methods"] = [kwargs["methods"].upper()]
            else:
                self.options["methods"] = [x.upper() for x in kwargs["methods"]]

        if "status_codes" in kwargs: 
            if not isinstance(kwargs["status_codes"], list):
                self.options["status_codes"] = [kwargs["status_codes"]]
            else:
                self.options["status_codes"] = kwargs["status_codes"]

        if "text" in kwargs: 
            if not isinstance(kwargs["text"], list):
                self.options["text"] = [kwargs["text"]]
            else:
                self.options["text"] = kwargs["text"]

        self.auditResultsPage = self._query()

        self.options['page_number'] = 0
        if self.auditResultsPage.total > 0:
            self.options['first_id'] = self.auditResultsPage.items[0]['id']

        return self.auditResultsPage

    def next(self):
        """Gets the next page of results using the parameters provided by the 
        :meth:`proknow.Audit.Audit.query` method.
        
        Returns:
            :class:`proknow.Audit.AuditResultsPage`

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.InvalidOperationError`: If this method is called before :meth:`proknow.Audit.Audit.query` is called.
        """
        if self.auditResultsPage is None:
            raise InvalidOperationError('\'Audit.query\' must be called before calling \'Audit.next\'')

        self.options['page_number'] += 1
        self.auditResultsPage = self._query()

        return self.auditResultsPage

    def _query(self): 
        _, results = self._requestor.post('/audit/events/search', json=self.options)
        
        return AuditResultsPage(self, results['total'], results['items'])

class AuditResultsPage(object):
    """
    This class represents a page of audit log query results. It's instantiated by the
    :meth:`proknow.Audits.Audit.query` method.

    Attributes:
        total (int): The total number of possible results for the given query, not the total of items in the object's item list.
        items (list of dict): A list of dictionaries to represent each item returned for the current page.
    """
    def __init__(self, audit, total, items):
        self._audit = audit
        self.total = total
        self.items = items
    
    def next(self):
        """Gets the next page of query results using the initial query parameters.

        Returns:
            :class:`proknow.Audit.AuditResultsPage`

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        return self._audit.next()
