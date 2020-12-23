Usage
=====

Read this guide to learn how to install ProKnow SDK and get started with your first script.

Installation
------------

Use ``pip`` to install::

    pip install --upgrade proknow

Basic Usage
-----------

To use the SDK, you'll need two important items:

* Base URL: This is the URL that will be used to make API requests to ProKnow. It's the first part of the web address you see when you are signed in to your ProKnow DS account. The form of this URL is typically ``https://your-domain.proknow.com``.
* API Token: You can generate an `API token <https://support.proknow.com/hc/en-us/articles/360019798893-Configuring-Your-Profile#managing-api-keys>`_ in the ProKnow DS user interface. Always keep your API Token secret. Once you have your ``credentials.json``, make note of the file path.

The code snippet below can be used to test your installation of the ``proknow`` package. Please be sure to replace ``https://example.proknow.com`` with your organization's Base URL described above, and replace ``./credentials.json`` with the path to your credentials file::

    from proknow import ProKnow

    pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
    workspaces = pk.workspaces.query()
    print("The workspaces are as follows:")
    for workspace in workspaces:
        print(workspace.name)

If an adaptation of the script above does not work for you see the troubleshooting section below.

Feature List
------------

For an updated picture of the pieces of the API that have been implemented in the Python SDK, please visit our `Feature List <https://github.com/proknow/proknow-python/wiki/Feature-List>`_ page on the project Wiki.

Troubleshooting
---------------

**Connection errors**

These can be caused by the failure to replace ``https://example.proknow.com`` as your ``base_url``. ``https://example.proknow.com`` is not a real endpoint and will not work. If you've already replaced the base URL, login to your ProKnow DS account and check to make sure it matches the base URL shown in the address bar.

If you are able to login to your ProKnow DS account and have verified that the base URLs match, there is also a chance that your organization's firewall is configured to block traffic originating from unknown sources like your Python script. If this is the case please contact your IT department to request special permission for your script to access the ProKnow API from inside your organization's network.

**File not found errors**

If you specified a ``credentials_file`` in the ProKnow constructor, but are receiving a message saying that the file or directory does not exist, you may have a typo in your credentials file path. Correct the file path, and try again. Note that relative file paths are usually relative to the directory from which the ``python`` executable is being invoked.

**Type or Assertion errors**

These indicate that you've provided invalid parameters to the ``ProKnow`` contructor. The error message can usually point you in the right direction. Correct the parameters, and try again.

**Copying examples without modification**

The examples shown throughout this documentation are meant to be representative and are not likely to work without modification. Let's take a look at the example for the method :meth:`proknow.Patients.PatientItem.set_metadata`::

    from proknow import ProKnow

    pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
    patients = pk.patients.lookup("Clinical", ["HNC-0522c0009"])
    patient = patients[0].get()
    meta = patient.get_metadata()
    meta["Genetic Type"] = "Type II"
    patient.set_metadata(meta)
    patient.save()

This script will not work in your set up for several reasons:

* Your ``base_url`` for your ProKnow account is not ``https://example.proknow.com``.
* Your ``credentials.json`` file may not be located at the path "./credentials.json."
* You probably do not have a patient with the MRN "HNC-0522c0009" in a workspace called "Clinical."
* You probably do not have a custom metric called "Genetic Type."

If you run into problems while running your script, examine the error message and make sure you didn't copy a code example without making the proper modifications. Values may need to be replaced or additional setup code may need to be added before the code you copied in order for your script to function properly.

Guides
------


.. toctree::
   :maxdepth: 2

   usage/computed_metrics
   usage/find_methods
   usage/contouring_data
   usage/dose_analysis
   usage/pydicom_primer
   usage/scorecard_objectives
   usage/patient_tasks
