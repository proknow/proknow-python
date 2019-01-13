Usage
=====

Read this guide to learn how to install ProKnow SDK and get started with your first script.

Installation
------------

Use ``pip`` to install::

	pip install proknow

Basic Usage
-----------

To use the SDK, you'll need to generate an `API token <https://support.proknow.com/article/165-configuring-your-profile#api-keys>`_ in the ProKnow DS user interface. Once you have a credentials file, use it in your script to create an instance of the main ProKnow class::

	from proknow import ProKnow

	pk = ProKnow('https://example.proknow.com', credentials_file="./credentials.json")
	workspaces = pk.workspaces.query()
	print("The workspaces are as follows:")
	for workspace in workspaces:
		print(workspace.name)
