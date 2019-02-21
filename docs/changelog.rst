Release History
===============

v0.4.1
------

**Disclaimer**

All releases in the v0.x.x series are subject to breaking changes from one version to another. After the release of v1.0.0, this project will be subject to `semantic versioning <http://semver.org/>`_.

**Bug Fixes**

This release attempts to fix installation errors for users running python 2. According to `this issue <https://github.com/Azure/azure-storage-python/issues/36>`_, wheels cannot (or should not) be marked as universal if it or one of its dependencies installs a package based on whether the python version is 2 or 3. For the ``proknow`` package, the dependency ``requests-futures`` installs the package ``futures`` if the python version is less than 3.2.

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
