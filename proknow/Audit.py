__all__ = [
    'Audit',
]

import copy

class Audit(object):
    """
    This class should be used to interact with the audit logs in a Proknow organization. It is
    instantiated for you as an attribute of the :class:`proknow.ProKnow.ProKnow` class.
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
    
    def query(self, **kwargs):
        """Queries for audit logs.

        Parameters:
            options (dict): Dictionary of one or more of the following query parameters
            page_size (int): (Default is 25) The number of items for each page
            start_time (datetime): Start time cut off for whole query
            end_time (datetime): End time cut off for whole query
            types (str or list): List of event types
            user_id (str): ID of events' enacting user
            user_name (str): User name of events' enacting user
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
            :class:`proknow.Audit.AuditResultsPage`: An object representing a page of query results

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        
        Example:
            This example shows how to query for all events in a workspace called "Clinical"::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                clinicalResults = pk.audit.query(workspace_name="Clinical")
                while len(clinicalResults.items) > 0:
                    for item in clinicalResults.items:
                        print(item)
                    clinicalResults = clinicalResults.next()
        """
        if "options" in kwargs: 
            options = kwargs["options"]
        else:
            options = {}

            if "page_size" in kwargs: options["page_size"] = kwargs["page_size"]
            if "start_time" in kwargs: options["start_time"] = kwargs["start_time"].isoformat()
            if "end_time" in kwargs: options["end_time"] = kwargs["end_time"].isoformat()
            if "user_id" in kwargs: options["user_id"] = kwargs["user_id"] 
            if "user_name" in kwargs: options["user_name"] = kwargs["user_name"]
            if "patient_id" in kwargs: options["patient_id"] = kwargs["patient_id"]
            if "patient_name" in kwargs: options["patient_name"] = kwargs["patient_name"]
            if "patient_mrn" in kwargs: options["patient_mrn"] = kwargs["patient_mrn"]
            if "workspace_id" in kwargs: options["workspace_id"] = kwargs["workspace_id"]
            if "workspace_name" in kwargs: options["workspace_name"] = kwargs["workspace_name"]
            if "collection_id" in kwargs: options["collection_id"] = kwargs["collection_id"]
            if "resource_id" in kwargs: options["resource_id"] = kwargs["resource_id"]
            if "resource_name" in kwargs: options["resource_name"] = kwargs["resource_name"] 
            if "classification" in kwargs: options["classification"] = kwargs["classification"].upper() 
            if "uri" in kwargs: options["uri"] = kwargs["uri"] 
            if "user_agent" in kwargs: options["user_agent"] = kwargs["user_agent"]
            if "ip_address" in kwargs: options["ip_address"] = kwargs["ip_address"]

            if "types" in kwargs: 
                if not isinstance(kwargs["types"], list):
                    options["types"] = [kwargs["types"]]
                else:
                    options["types"] = kwargs["types"]

            if "methods" in kwargs: 
                if not isinstance(kwargs["methods"], list):
                    options["methods"] = [kwargs["methods"].upper()]
                else:
                    options["methods"] = [x.upper() for x in kwargs["methods"]]

            if "status_codes" in kwargs: 
                if not isinstance(kwargs["status_codes"], list):
                    options["status_codes"] = [kwargs["status_codes"]]
                else:
                    options["status_codes"] = kwargs["status_codes"]

            if "text" in kwargs: 
                if not isinstance(kwargs["text"], list):
                    options["text"] = [kwargs["text"]]
                else:
                    options["text"] = kwargs["text"]

        return self._query(options)

    def _query(self, options): 
        _, results = self._requestor.post('/audit/events/search', json=options)
        
        return AuditResultsPage(self, options, results['total'], results['items'])

class AuditResultsPage(object):
    """
    This class represents a page of audit log query results. It's instantiated by the
    :meth:`proknow.Audit.Audit.query` method.

    Attributes:
        total (int): The total number of possible results for the given query, not the total of items in the object's item list.
        items (list of dict): A list of dictionaries to represent each item returned for the current page.

            Item Keys:
                * id: The ID of the event
                * timestamp: Time of event
                * user_id: User ID of event's enacting user
                * user_name: User name of event's enacting user
                * patient_id: ID of patient
                * patient_name: Name of patient
                * patient_mrn: Medical record number of patient
                * resource_id: ID of a resource
                * resource_name: Name of a resource
                * workspace_id: ID of workspace in which events took place
                * workspace_name: Name of workspace in which events took place
                * collection_id: ID of a collection
                * type: Event type (e.g. 'workspace_created')
                * classification: 'HTTP' or 'AUTH'
                * method: HTTP method: 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', or 'PATCH'
                * uri: Uri that event took place (e.g. '/metrics/custom')
                * user_agent: User Agent attributed to event (e.g. Browser User Agent)
                * ip_address: IP Address attributed to event
                * status_code: Status code of event (e.g. 200)
                * data: Request data
    """

    def __init__(self, audit, options, total, items):
        self._audit = audit
        self._options = options
        self.total = total
        self.items = items
        if "page_number" not in self._options:
            self._options["page_number"] = 0
        if "first_id" not in self._options and total > 0:
            self._options["first_id"] = items[0]["id"]
    
    def next(self):
        """Gets the next page of query results using the initial query parameters.

        Returns:
            :class:`proknow.Audit.AuditResultsPage`: A new object representing the next page of query results relative to the current page. 

        Raises: 
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
        """
        options = copy.deepcopy(self._options)
        options["page_number"] += 1
        return self._audit.query(options=options)
