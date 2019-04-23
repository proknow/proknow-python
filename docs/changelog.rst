Release History
===============

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
