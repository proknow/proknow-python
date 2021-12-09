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
    
    def query(self, page_size=25, start_time=None, end_time=None,
        type=None, user_name=None, patient_name=None, classification=None, 
        method=None, uri=None, user_agent=None, ip_address=None, status_code=None, 
        workspace_id=None, resource_id=None):

        """Queries for audit logs.

        Parameters:
            page_size (int): The number of items for each page
            start_time (datetime): Start date cut off for whole query
            end_time (datetime): End date cut off for whole query
            type (str): Type of event
            user_name (str): Name of event's enacting user
            patient_name (str): Name of patient
            classification (str): 'HTTP" or 'AUTH'
            method (str): HTTP Method: 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', or 'PATCH'
            uri (str): Filter by the uri that event took place (e.g. '/metrics/custom')
            user_agent (str): User Agent attributed to event (e.g. Browser User Agent)
            ip_address (str): IP Address attributed to event
            status_code (int): Status code of event (e.g. 200)
            workspace_id (str): ID of workspace in which event took place
            resource_id (str): ID of resource

        Returns:
            A :class:`proknow.Audit.AuditResultsPage` object, representing a page of query results

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """

        self.options = dict()
        if page_size is not None: self.options["page_size"] = page_size
        if start_time is not None: self.options["start_time"] = start_time.isoformat()
        if end_time is not None: self.options["end_time"] = end_time.isoformat()
        if type is not None: self.options["type"] = type 
        if user_name is not None: self.options["user_name"] = user_name 
        if patient_name is not None: self.options["patient_name"] = patient_name 
        if classification is not None: self.options["classification"] = classification.upper() 
        if method is not None: self.options["method"] = method.upper() 
        if uri is not None: self.options["uri"] = uri 
        if user_agent is not None: self.options["user_agent"] = user_agent
        if ip_address is not None: self.options["ip_address"] = ip_address
        if status_code is not None: self.options["status_code"] = status_code
        if workspace_id is not None: self.options["workspace_id"] = workspace_id
        if resource_id is not None: self.options["resource_id"] = resource_id

        self.auditResultsPage = self._query()

        self.options['page_number'] = 0
        if self.auditResultsPage.total > 0:
            self.options['first_id'] = self.auditResultsPage.items[0]['id']

        return self.auditResultsPage

    def next(self):
        """Gets the next page of results using the parameters provided by the 
        :meth:`proknow.Audit.Audit.query` method.
        
        Returns :
            :class:`proknow.Audit.AuditResultsPage`

        Raises :
            :class:`proknow.Exceptions.InvalidOperationError`: If the method is called before query is called.
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        if self.auditResultsPage is None:
            raise InvalidOperationError('Next was called when there is no initial query!')
        self.options['page_number'] += 1
        self.auditResultsPage = self._query()
        return self.auditResultsPage


    def _query(self): 
        print(self.options)
        _, results = self._requestor.post('/audit/events/search', json=self.options)
        
        return AuditResultsPage(self, results['total'], results['items'])

class AuditResultsPage(object):
    """

    This class represents a page of audit log query results. It's instantiated by the
    :meth:`proknow.Audits.Audit.query` method.

    Attributes:
        total (int): The total number of possible results for the given query.
        items (list of dict): A list of dictionaries to represent each item returned for the current page.
    """
    def __init__(self, audit, total, items):
        self._audit = audit
        self.total = total
        self.items = items
    
    def next(self):
        """Gets the next page of query results using the initial parameters

        Returns:
            :class:`proknow.Audit.AuditResultsPage`

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        return self._audit.next()

