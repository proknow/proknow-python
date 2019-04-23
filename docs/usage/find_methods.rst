.. _find-methods:

Using Find Methods
==================

Basics
------

Within the ProKnow Python SDK, there are many classes that support a ``find`` method for performing a local search over a list of items to find an item matching some criteria. This is can be useful when you know something like the name of an item but not its id. These methods typically have the following signature::

    def find(predicate=None, **props):

The ``predicate`` is a function that is passed an item as input and which should return a bool indicating whether the item is a match. The ``**props`` argument is a dictionary of keyword arguments that may include any item attribute to use to find a matching item. Note that ``predicate`` and any additional keywords are always optional. For example, you can provide no arguments to the :meth:`proknow.Users.Users.find` method, which will always return the value ``None``::

    user = pk.users.find()
    print(user)

    # Output: None

Other examples of the ``find`` method like :meth:`proknow.Patients.Patients.find` have other, sometimes required, parameters. However, the ``predicate`` and additional keywords are still optional, and omitting them will return the value ``None`` (just like in the example above)::

    patient = pk.patients.find("Research")
    print(patient)

    # Output: None

Not providing any parameters to these methods isn't very useful of course. In the next two sections, we'll expore how to use each of these parameters.

Keyword Arguments
-----------------

Let's start with the additional keyword arguments. Each arguments is tested against the ``data`` attribute of the instance, which is a dictionary of key-value pairs. Here is an example::

    user = pk.users.find(name="Terence Arnold")

The examples above demonstrates how to find a user whose name matches "Terance Arnold." Note that the name must match exactly. We are free to include more than one property. For example::

    user = pk.users.find(name="Terence Arnold", active=False)

This example finds a user whose name matches "Terance Arnold" AND whose ``active`` property is ``False``. In other words, a user will only be considered a match if its properties match all of the provided keyword arguments.

You might be wondering what arguments are allowed. While that depends on the class in question, you can easily find a list of properties for an item by printing the ``data`` attribute. Use the following 3-step process.

1. Query for a list of summary or item objects.
2. Pick any item from the list (doesn't matter which).
3. Print the value of the ``data`` attribute to the console.

Here's an example using the :class:`proknow.Users.Users` class::

    users = pk.users.query()   # Step 1
    first = user[0]            # Step 2
    print(first.data)          # Step 3
    print(first.data.keys())   # Step 3 (alternative if you're not interested in example values)

    # Example Output:
    # {'id': '5c463a6c04005a992cc16b29f9a7637b', 'email': 'kburnett@proknow.com', 'name': 'Kyle Burnett', 'active': True, 'federated': False, 'created_at': '2019-01-21T21:32:29.724Z'}
    # dict_keys(['id', 'email', 'name', 'active', 'federated', 'created_at'])

Predicate
---------

Keyword arguments are useful for finding items that match properties of objects exactly. But let's say you wanted to implement a user name search that used a "fuzzy matching" algorithm to search for users by name (e.g., using the `Fuzzy Python module <https://pypi.org/project/Fuzzy/>`_). Let's look at an example::

    import fuzzy  # (1)

    soundex = fuzzy.Soundex(4)  # (2)

    def predicate(user):  # (3)
        return soundex(user.data["name"]) == soundex("Terence Arnold")

    user = pk.users.find(predicate)  # (4)

In line (1), we're importing the fuzzy module, and in line (2) we're using that module to construct a Soundex function we can use later. Line (3) defines our predicate function. This function takes a user as input, extracts, the name of the user, computes its "Soundex" value, and compares that value for equality to the "Soundex" value for "Terence Arnold." Users with a name that sounds like "Terence Arnold" will result in the value of ``True`` (``False`` otherwise). Finally, in line (4) we pass the predicate as an argument to the ``find`` method. At the end of this code snippet, ``user`` will be assigned the first user whose name sounds approximately like "Terence Arnold" (or ``None`` if no such user exists).

The predicate function above can be transformed into a single line using a lambda expression (anonymous function)::

    import fuzzy

    soundex = fuzzy.Soundex(4)

    user = pk.users.find(lambda user: soundex(user.data["name"]) == soundex("Terence Arnold"))

Other Important Points
----------------------

**A predicate and keyword arguments may be used together.**

A predicate and keyword argument may be used together. In this case, an item is only considered a match when the ``predicate`` returns ``True`` AND match against all the provided keyword arguments. In the following example, the first user with a name that sounds like "Terence Arnold" and whose ``active`` property is ``True`` will be returned.

**The method proknow.Patients.PatientItem.find_entities behaves in a similar fashion.**

The method :meth:`proknow.Patients.PatientItem.find_entities` behaves similarly to the ``find`` method describes above except that the ``find_entities`` method traverses through each entity in the entity hierarchy within a PatientItem to find find matching entities. It returns a list of all matching entities whereas the ``find`` method returns the first matching item it finds. To find a list of the properties available for the ``find_entities`` method, we can use the ``find_entities`` method on a sample patient to give us a flattened list of entities, which we'll print using the pprint module. The example below assumes you already have a patient module available as ``patient``::

    from pprint import pprint

    entities = patient.find_entities(lambda entity: True)
    for entity in entities:
        pprint(entity.data, depth=1)

    # Example Output:
    # {'description': 'CTs from rtog conversion',
    #  'entities': [...],
    #  'frame_of_reference': '1.3.6.1.4.1.22213.2.26556.1',
    #  'id': '5cbf3f1989000ca6998849a4870a120c',
    #  'image_set_id': None,
    #  'metadata': {},
    #  'modality': 'CT',
    #  'parent_uid': None,
    #  'plan_id': None,
    #  'series_uid': '1.3.6.1.4.1.22213.2.26556.2',
    #  'status': 'completed',
    #  'structure_set_id': None,
    #  'study': '5cbf3f198780503c2479bc74bbae8872',
    #  'type': 'image_set',
    #  'uid': '1.3.6.1.4.1.22213.2.26556.2'}
    # {'description': 'RTOG_CONV',
    #  'entities': [...],
    #  'frame_of_reference': '1.3.6.1.4.1.22213.2.26556.1',
    #  'id': '5cbf3f1a0bc019af648ad8cc07810638',
    #  'image_set_id': '5cbf3f1989000ca6998849a4870a120c',
    #  'metadata': {},
    #  'modality': 'RTSTRUCT',
    #  'parent_uid': '1.3.6.1.4.1.22213.2.26556.2',
    #  'plan_id': None,
    #  'series_uid': '1.3.6.1.4.1.22213.2.26556.3',
    #  'status': 'completed',
    #  'structure_set_id': None,
    #  'study': '5cbf3f198780503c2479bc74bbae8872',
    #  'type': 'structure_set',
    #  'uid': '1.3.6.1.4.1.22213.2.26556.3.1'}
    # {'description': 'fx1hetero',
    #  'entities': [...],
    #  'frame_of_reference': '1.3.6.1.4.1.22213.2.26556.1',
    #  'id': '5cbf3f257080853d58e7481bf2d8b889',
    #  'image_set_id': '5cbf3f1989000ca6998849a4870a120c',
    #  'metadata': {},
    #  'modality': 'RTPLAN',
    #  'parent_uid': '1.3.6.1.4.1.22213.2.26556.3.1',
    #  'plan_id': None,
    #  'series_uid': '1.3.6.1.4.1.22213.2.26556.4.1',
    #  'status': 'completed',
    #  'structure_set_id': '5cbf3f1a0bc019af648ad8cc07810638',
    #  'study': '5cbf3f198780503c2479bc74bbae8872',
    #  'type': 'plan',
    #  'uid': '1.3.6.1.4.1.22213.2.26556.4.1.1'}
    # {'description': 'RT Dose - fx1hetero',
    #  'entities': [],
    #  'frame_of_reference': '1.3.6.1.4.1.22213.2.26556.1',
    #  'id': '5cbf3f25bc80d1f1ff64a1d79d8950d9',
    #  'image_set_id': '5cbf3f1989000ca6998849a4870a120c',
    #  'metadata': {},
    #  'modality': 'RTDOSE',
    #  'parent_uid': '1.3.6.1.4.1.22213.2.26556.4.1.1',
    #  'plan_id': '5cbf3f257080853d58e7481bf2d8b889',
    #  'series_uid': '1.3.6.1.4.1.22213.2.26556.5.1',
    #  'status': 'completed',
    #  'structure_set_id': '5cbf3f1a0bc019af648ad8cc07810638',
    #  'study': '5cbf3f198780503c2479bc74bbae8872',
    #  'type': 'dose',
    #  'uid': '1.3.6.1.4.1.22213.2.26556.5.1.1'}
