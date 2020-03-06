.. _dose-analysis:

Dose Analysis
=============

The dose analysis object is defined as follows::

    {
      "max_dose": 75.49002838134766,         # The maximum dose over the entire dose grid
      "max_dose_loc": [                      # The coordinates of the max dose within the dose grid
        4.2400054931640625,
        -584.0599975585938,
        -351.6500244140625
      ],
      "volume": 35281.664000000004,          # The volume of the dose grid
      "plan": {                              # Additional plan details
        "estimated_delivery_time": null,
        "cumulative_meterset": 0
      },
      "curve": [                             # Curve data rendered as an array of two-element arrays
        [ 0, 100 ],                          # i.e., [[x_1, y_1], [x_2, y_2], ...]
        [ 0.01, 32.37180709838867 ],
        ...
      ],
      "rois": [                              # The list of ROIs included in the analysis
        {
          "id": "5e5ebb801140e067f327445dfeac3888",
          "name": "BRAIN_STEM",                       # The name of the ROI
          "dose_grid_bound": true,                    # Whether the structure is entirely enclosed within the dose grid
          "integral_dose": 339.91525629891083,        # The integral dose (Gy * cc) delivered to the ROI
          "max_dose": 43.51894,                       # The maximum dose to the ROI
          "max_dose_loc": [                           # The coordinates of the maximum dose within the ROI
            -0.5,
            -451.20001220703125,
            -404.6000061035156
          ],
          "mean_dose": 17.549470901489258,            # The mean dose to the ROI
          "min_dose": 2.232161521911621,              # The minimum dose to the ROI
          "min_dose_loc": [                           # The coordinates of the minimum dose within the ROI
            -8.199999809265137,
            -415.20001220703125,
            -424
          ],
          "volume": 19.368974609375,                  # The volume of the ROI
          "curve": [                                  # Curve data rendered as an array of two-element arrays
            [ 0, 100 ],                               # i.e., [[x_1, y_1], [x_2, y_2], ...]
            [ 2.23, 100 ],
            ...
          ]
        }
      ],
      ...
    }
