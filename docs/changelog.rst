Release History
===============

v0.18.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to query for audit logs using the ``proknow.Audit.Audit`` class

v0.17.1
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fix bug preventing client from getting details about plan entities created in ProKnow

v0.17.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to create a plan with the ``proknow.Patients.PatientItem.create_plan`` method.
* Entity scorecards have been replaced with patient scorecards.

**Bug Fixes**

* Updated link in usage documentation related to generating API keys.
* Some examples involving editing structure sets were not properly creating a draft before attempting attempting edits.
* Fixed an issue that could cause upload processing updates to occasionally be missed resulting in a timeout error.

v0.16.3
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fixed bug that preventing users without the organization-level read collections permission from interacting with organization collections

v0.16.2
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Failed connection attempts will now properly retry a configurable number of times

v0.16.1
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Uploads initiated from a patient now properly specify the scope

v0.16.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added support for adding computed metrics for a dose entity
* Added support for query computed metrics results for a dose entity
* Added support for retrieving plan delivery information for a plan entity
* Added support for updating a list of entities within a workspace
* Added support for updating the parent of an entity

**Bug Fixes**

* Fixed miscellaneous issues in the documentation

v0.15.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added support for private roles
* Added support for retrieving analysis data for a dose entity

**Bug Fixes**

* Fixed miscellaneous issues in the documentation

v0.14.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to create a structure set
* Added ability to refresh a patient item

v0.13.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to create, delete (i.e., hide), and query patient tasks

v0.12.1
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fixed documentation for several method examples in the ``proknow.Patients.EntityItem`` class

v0.12.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to get and set entity metadata and save entity changes (description and metadata)

v0.11.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to upload files without waiting for each file to reach a terminal state

v0.10.2
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fixed issue where the patient lookup method could fail if an MRN that does not exist is provided.

v0.10.1
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fixed issue where uploading a directory could fail if there was a file in the directory with a size of 0

v0.10.0
-------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ability to get image and dose slice data

v0.9.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added ``Scorecard Objectives`` to explain how to include objectives in scorecard templates, patient scorecards, and collection scorecards
* Achieved 100% code coverage
* Improved behavior of the ``resolve_by_name`` methods to perform in a case insensitive manner

**Bug Fixes**

* Fixed issue where the ``get`` method for an ``EntitySummary`` could fail if the entity had not finished processing

v0.8.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Added support for deleting entities
* Added support for interacting with scorecard templates
* Added support for getting the current user session
* Added support for uploading files directly to a patient
* Reimplemented upload mechanism to utilize the concurrent.futures (`futures` for Python 2) instead of `requests-futures` module
* Updated Roles for new ProKnow DS version changes (v1.10.0).

v0.7.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Improved code coverage
* Added support for interacting with scorecards for collections
* Renamed ``CollectionItemPatients`` and ``CollectionItemPatientSummary`` classes to ``CollectionPatients`` and ``CollectionPatientSummary``, respectively
* Implemented paging and the search parameter in ``Patients.query`` method

**Bug Fixes**

* Fixed issues in some code examples

v0.6.1
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Clarified documentation for the patient date and patient sex fields
* Updated ``CollectionItemPatients.query`` method to support API changes in ProKnow DS v1.8.0

v0.6.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features and Enhancements**

* Augmented ``StructureSetItem`` class to include methods for interacting with ROIs, versions, and structure set drafts. New classes ``StructureSetRoiItem``, ``StructureSetRoiData``, ``StructureSetVersions``, and ``StructureSetVersionItem`` were created in support of these features.
* Added additional guides:

  * Using Find Methods
  * Using Contouring Data
  * pydicom Primer

* Improved code coverage
* Added ``LOCK_RENEWAL_BUFFER`` argument and attribute to main ProKnow class

v0.5.1
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* The PyPi package for v0.5.0 was not built properly. This version addresses that issue and should be used in place of v0.5.0.

v0.5.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features & Enhancements**

* Added new classes in the ``Patients`` module for interacting with entity scorecards
* Improved code coverage

v0.4.1
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

* Fixed bug in ``CollectionItemPatients.query`` affecting workspace collections
* Fixed typo in create collections documentation example

v0.4.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features & Enhancements**

* ``Collections`` module for interacting with collections
* Renamed ``metric_type`` argument in the ``CustomMetrics.create`` method to ``type``

v0.3.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features & Enhancements**

* Changed the following method names:

  * ``resolveById`` to ``resolve_by_id``
  * ``resolveByName`` to ``resolve_by_name``

* Improved documentation throughout
* ``Uploads`` module for initiating new uploads
* Implemented testing
* Implemented classes for ``ImageSetItem`` and ``StructureSetItem`` in the ``Patients`` module.

**Bug Fixes**

* Fixed bug in ``Workspaces.resolve_by_id`` method
* Fixed bug in ``CustomMetricItem.save`` method
* Fixed bug in ``Patients.create`` method

v0.2.0
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**New Features & Enhancements**

* Added ``resolve``, ``resolveById``, and ``resolveByName`` methods to ``Workspace`` class
* Added ``stream`` method to ``Requestor`` class
* New ``Exceptions`` module for errors specific to the ProKnow DS - Python SDK.
* ``CustomMetrics`` module for interacting with organization custom metrics. This module is also used by the ``Patients`` module when getting and setting metadata.
* ``Patients`` module for interacting with patient data (including studies and entities).
* Change implementation of ``.find`` method throughout to use the signature ``(self, predicate=None, **props)``.
* Renamed ``identifier`` arguments as ``workspace_id``, ``role_id``, ``user_id``, etc.

v0.1.0
------

**New Features & Enhancements**

* Base ``ProKnow`` module that may be initialized with API credentials and used to access ProKnow services
* ``Requestor`` helper module for constructing and issuing API requests
* Identity and Access Management (IAM) Modules

  * ``Workspaces``
  * ``Roles``
  * ``Users``
