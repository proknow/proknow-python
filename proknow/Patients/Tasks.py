import six
import time
from datetime import datetime

from ..Exceptions import TimeoutExceededError

class Tasks(object):
    """

    This class should be used to interact with the tasks for a patient. It is instantiated for you
    as an attribute of the :class:`proknow.Patients.PatientItem` class.

    """

    def __init__(self, patients, workspace_id, patient_id):
        """Initializes the Tasks class.

        Parameters:
            patients (proknow.Patients.Patients): The Patients instance that is instantiating the
                object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the tasks belong.
        """
        self._patients = patients
        self._requestor = self._patients._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id

    def _query(self, hidden=False, wait=False, wait_start=None):
        wait_start = datetime.utcnow()
        params = {}
        if hidden is True:
            params["hidden"] = "true"
        while True:
            _, tasks = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks', params=params)
            if wait is True:
                for task in tasks:
                    if task["status"] not in ("completed", "failed"):
                        if (datetime.utcnow() - wait_start).total_seconds() > 30: # pragma: no cover
                            print(task["status"], (datetime.utcnow() - wait_start).total_seconds())
                            raise TimeoutExceededError("Timeout of 30 seconds elapsed while waiting for tasks to become resolved")
                        else:
                            break
                else:
                    return tasks
                time.sleep(0.5)
            else:
                return tasks

    def create(self, body):
        """Creates a patient task.

        Parameters:
            body (dict): The task creation parameters. For information on how to construct this
                parameter, please check out the :ref:`patient-tasks` guide.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to create a task for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234").get()
                operands = [{
                    "type": "dose",
                    "id": dose.id
                } for dose in patient.find_entities(type="dose")]
                patient.tasks.create({
                    "type": "dose_composition",
                    "name": "Dose Composition",
                    "operation": {
                        "type": "addition",
                        "operands": operands
                    }
                })
        """
        _, task = self._requestor.post('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks', json=body)
        return self.get(task["id"]);

    def delete(self, task_id):
        """Deletes the patient task.

        Parameters:
            task_id (str): The id of the patient task to delete.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to delete a task for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234").get()
                patient.tasks.delete('5c4b4c52a5c058c3d1d98ac194d0200f')
        """
        assert isinstance(task_id, six.string_types), "`task_id` is required as a string."
        self._requestor.delete('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks/' + task_id)

    def get(self, task_id):
        """Gets the patient task.

        Parameters:
            task_id (str): The id of the patient task to get.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to get a task for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234").get()
                task = patient.tasks.get('5c4b4c52a5c058c3d1d98ac194d0200f')
        """
        _, task = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks/' + task_id)
        return TaskItem(self, self._workspace_id, self._patient_id, task)

    def query(self, hidden=False, wait=False):
        """Queries the patient tasks.

        Parameters:
            hidden (bool, optional): Whether hidden tasks should be included in the results
                (defaults=False).
            wait (bool, optional): Whether to wait for tasks to reach a resolved state before
                terminating (default=False).

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
                waiting for the tasks to complete.

        Example:
            The following example shows how to query tasks for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234").get()
                tasks = patient.tasks.query()
        """
        return [TaskSummary(self, self._workspace_id, self._patient_id, task) for task in self._query(hidden, wait)]

class TaskSummary(object):
    """

    This class represents a summary view of a patient task. It's instantiated by the
    :meth:`proknow.Patients.Tasks.query` method to represent each of the patient tasks returned in a
    query result.

    Attributes:
        id (str): The id of the patient (readonly).
        data (dict): The summary representation of the patient task as returned from the API
            (readonly).

    """

    def __init__(self, tasks, workspace_id, patient_id, task):
        """Initializes the PatientSummary class.

        Parameters:
            tasks (proknow.Patients.Tasks): The Tasks instance that is instantiating the object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the task belongs.
            task (dict): A dictionary of task attributes.
        """
        self._tasks = tasks
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = task["id"]
        self._data = task

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def get(self):
        """Gets the complete representation of the patient task.

        Returns:
            :class:`proknow.Patients.TaskItem`: An object representing a patient task.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to turn a list of TaskSummary objects into a list of
            TaskItem objects::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234")
                tasks = [task.get() for task in patient.tasks.query()]
        """
        return self._tasks.get(self._id)

class TaskItem(object):
    """

    This class represents a patient tasks. It's instantiated by the :class:`proknow.Patients.Tasks`
    class as a complete representation of a patient task.

    Attributes:
        id (str): The id of the patient task (readonly).
        data (dict): The complete representation of the patient task as returned from the API
            (readonly).
    """

    def __init__(self, tasks, workspace_id, patient_id, task):
        """Initializes the TaskItem class.

        Parameters:
            tasks (proknow.Patients.Tasks): The Tasks instance that is instantiating the object.
            workspace_id (str): The id of the workspace to which the patient belongs.
            patient_id (str): The id of the patient to which the task belongs.
            task (dict): A dictionary of task attributes.
        """
        self._tasks = tasks
        self._requestor = self._tasks._requestor
        self._workspace_id = workspace_id
        self._patient_id = patient_id
        self._id = task["id"]
        self._data = task

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    def delete(self):
        """Deletes the patient task.

        Raises:
            :class:`proknow.Exceptions.HttpError`: If the HTTP request generated an error.

        Example:
            The following example shows how to delete the tasks for a patient::

                from proknow import ProKnow

                pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
                patient = pk.patients.find("Clinical", mrn="1234")
                for task in patient.tasks.query():
                    task.get().delete()
        """
        self._tasks.delete(self._id)
        _, task = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks/' + self._id)
        self._data = task

    def wait(self):
        """Wait for the patient task to be completed

        Raises
            :class:`proknow.Exceptions.TimeoutExceededError`: If the timeout was exceeded while
            waiting for the uploads to complete.
        """
        wait_start = datetime.utcnow()
        while True:
            _, task = self._requestor.get('/workspaces/' + self._workspace_id + '/patients/' + self._patient_id + '/tasks/' + self._id)
            if task["status"] == "completed" or task["status"] == "failed":
                self._data = task
                break
            elif (datetime.utcnow() - wait_start).total_seconds() > 30: # pragma: no cover
                raise TimeoutExceededError("Timeout of 30 seconds elapsed while waiting for task to become resolved")
            else:
                time.sleep(0.5)

