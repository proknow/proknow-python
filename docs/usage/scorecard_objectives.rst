.. _scorecard-objectives:

Scorecard Objectives
====================

Scorecard objectives may be defined for each metric in a scorecard. Scorecard objectives are comprised of 2 to 10 levels, where each level defines a label (a string up to 64 characters in length), a color (represented as a 3-element array of RGB values), and max/min properties (which may or may not be defined according to the rules below). The focus of this article is the meaning of the "min" and "max" values.

Remember that scorecard objectives define a set of performance bins to which a metric value (whether computed or custom) is assigned based on the defined ranges of each performance bin. The definition for the basic "Standard Pass/Fail (Pass Min)" objectives looks something like this::

    [{
        "label": "PASS",
        "color": [18, 191, 0],
        "max": 1
    }, {
        "label": "FAIL",
        "color": [255, 0, 0]
    }]

The "max" property with a value of 1 is provided in the PASS performance bin. This indicates that values up to a *maximum* of 1 will fall into the PASS performance bin for that metric, while values greater than 1 will fall into the FAIL performance bin. If instead we wish for a value of 1 to fall into the FAIL performance bin, we could define the metric objective in this manner::

    [{
        "label": "PASS",
        "color": [18, 191, 0]
    }, {
        "label": "FAIL",
        "color": [255, 0, 0],
        "min": 1
    }]

This indicates that values less than 1 will fall into the PASS perfomance bin, while values from a *minimum* of 1 and greater will fall into the FAIL perfomance bin. In this manner the "min" and "max" properties define which performance bin a metric value evaluates to **if the metric value is exactly equal to a threshold value**.

When designing a valid objectives configuration, it is important to keep in mind the following rules.

1. The first performance bin may only have a ``"max"``. It cannot have a ``"min"``.
2. The last performance bin may only have a ``"min"``. It cannot have a ``"max"``.
3. Neighboring performance bins X and Y, where the X bin comes before the Y bin, must define either a ``"max"`` for X or a ``"min"`` for Y (but not both).
4. Performance bin ranges must be non-zero.

Exercise 1
----------

Design objectives for a metric for the volume of an organ in which the organ is considered VERY SMALL if the organ is less than 8 (x < 8), SMALL if the organ is greater than or equal to 8 and less than 15 (8 ≤ x < 15), NORMAL if the organ is greater than or equal to 15 and less than or equal to 29 (15 ≤ x ≤ 29), LARGE if the organ is greater than 29 and less than or equal to 36 (29 < x ≤ 36), and VERY LARGE if the organ is greater than 36 (36 > x).

The solution is as follows::

    [{
        "color": [255, 0, 0],
        "label": "VERY SMALL"
    }, {
        "min": 8,
        "color": [255, 216, 0],
        "label": "SMALL"
    }, {
        "min": 15,
        "max": 29,
        "color": [24, 255, 0],
        "label": "NORMAL"
    }, {
        "max": 36,
        "color": [255, 216, 0],
        "label": "LARGE"
    }, {
        "color": [255, 0, 0],
        "label": "VERY LARGE"
    }]

Exercise 2
----------

A count of the number of ``"min"`` and ``"max"`` fields defined for a given metric's objectives should always be equal to what value (in terms of the number of performance bins, N). Note: This is a good way to determine if you have too many or too few ``"min"`` or ``"max"`` fields defined.

Solution: N - 1
