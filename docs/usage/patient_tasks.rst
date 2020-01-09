.. _patient-tasks:

Patient Tasks
=============

Dose Composition
----------------

The top-level fields of a dose composition task are ``"type"``, ``"name"``, and ``"operation"``. ``"type"`` must have the value ``"dose_composition"``. ``"name"`` must be a string up to 64 characters in length. The ``"operation"`` field may be an object representing an addition operation, a multiplication operation, a division operation, or a dose entity::

    {
      "type": "dose_composition",
      "name": "Dose Composition",
      "operation": {
        ...
      }
    }

The dose operation type is the simplest operation type. At minimum it consists of an object with the fields ``"type"`` and ``"id"``. For a dose, ``"type"`` should have the value "dose", and ``"id"`` should be the id of the entity.

The remaining operation types, on the other hand, consist of an object with the fields ``"type"`` and ``"operands"``. For the addition, multiplication, and division operations, the ``"type"`` should have the value "addition," "multiplication," and "division," respectively. The ``"operands"`` field should be an array of nested operations. At least two operands are required for addition, and exactly two operands are required for multiplication and division. The term "primary operand" is used to denote the first operand of an operation.

All operation types may also specify the fields ``"offset"``, ``"scale"``, and ``"transformation"``. ``"offset"`` is a number representing the dose to add to each voxel in the resulting dose grid. ``"scale"`` is a number by which to scale each dose voxel. Finally, ``"transformation"`` is an object with the fields ``"type"`` and ``"id"``. ``"type"`` should have the value ``"sro"``, and ``"id"`` should be the id of a spatial registration object that transforms the operand from its current frame of reference into the frame of reference of the parent operation's primary operand. Note that ``"transformation"`` should be provided if and only if the frame of references between the operand and the parent operation's primary operand are different.

Examples of dose compositions using the various operation types are produced below::

    # A dose composition that simply offsets the dose by +1 Gy
    {
      "type": "dose_composition",
      "name": "Dose Composition",
      "operation": {
        "type": "dose",
        "id": "755e070062740bde65cf95ed89e6c8fc",
        "offset": 1.0
      }
    }

    # A dose composition operation that scales the final result by 50%
    {
      "type": "dose_composition",
      "name": "Dose Composition",
      "operation": {
        "type": "addition",
        "operands": [{
          "type": "dose",
          "id": "755e070062740bde65cf95ed89e6c8fc",
        }, {
          "type": "dose",
          "id": "1875dda7af54c45f742638e1a6a3307a",
          "transformation": {
            "type": "sro",
            "id": "13f78cbec6800c2a1c1986359fa5ec31"
          }
        }],
        "scale": 0.5
      }
    }

    # A dose composition involving a nexted structure of all four operation types.
    {
      "type": "dose_composition",
      "name": "Dose Composition",
      "operation": {
        "type": "division",
        "operands": [{
          "type": "addition",
          "operands": [{
            "type": "multiplication",
            "operands": [{
              "type": "dose",
              "id": "d01ef294692b854edc1f2872581ee990"
            }, {
              "type": "dose",
              "id": "755e070062740bde65cf95ed89e6c8fc"
            }]
          }, {
            "type": "multiplication",
            "operands": [{
              "type": "dose",
              "id": "a16b19ef7374413aa27621b7561fbdbc"
            }, {
              "type": "dose",
              "id": "1875dda7af54c45f742638e1a6a3307a"
            }]
          }]
        }, {
          "type": "addition",
          "operands": [{
            "type": "dose",
            "id": "755e070062740bde65cf95ed89e6c8fc"
          }, {
            "type": "dose",
            "id": "1875dda7af54c45f742638e1a6a3307a"
          }]
        }]
      }
    }
