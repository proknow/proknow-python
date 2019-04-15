.. _computed-metrics:

Computed Metrics
================

Instructions
------------

The following list can be used when adding computed metrics to a scorecard or dose. Each item in the list corresponds to a different metric type, which is displayed in a nested list below the top-level item. The nested list below each metric item also displays the required arguments. For example, in order to compose a metric for "Dose (Gy) covering specified volume (%) of the specified structure," you need to specify *roi_name* and *arg_1* in the computed metric dict::

	{
		"type": "DOSE_VOLUME_PERCENT_ROI",
		"roi_name": "PTV",
		"arg_1": 99
	}

Here's another example with "Volume (%) of the specified structure covered by specified dose (Gy)" that uses *roi_name*, *arg_1*, and *arg_2*::

	{
		"type": "VOLUME_PERCENT_DOSE_RANGE_ROI",
		"roi_name": "BRAINSTEM",
		"arg_1": 0,
		"arg_2": 10
	}

Some computed metric types may not require any arguments at all::

	{
		"type": "MAX_DOSE"
	}

Metric List
-----------

.. include:: <isonum.txt>

* Dose (Gy) covering specified volume (%) of the specified structure

  * Type: ``DOSE_VOLUME_PERCENT_ROI``
  * Arguments: Dose (Gy) covering *arg_1* (%) of the *roi_name*

* Dose (Gy) covering specified volume (cc) of the specified structure

  * Type: ``DOSE_VOLUME_CC_ROI``
  * Arguments: Dose (Gy) covering *arg_1* (cc) of the *roi_name*

* Dose (Gy) covering the specified structure's total volume (cc) minus specified volume (cc)

  * Type: ``DOSE_VOLUME_MINUS_CC_ROI``
  * Arguments: Dose (Gy) covering the total volume (cc) minus *arg_1* (cc) of the *roi_name*

* Volume (cc) of the specified structure covered by specified dose (Gy)

  * Type: ``VOLUME_CC_DOSE_ROI``
  * Arguments: Volume (cc) of the *roi_name* covered by *arg_1*

* Volume (%) of the specified structure covered by specified dose (Gy)

  * Type: ``VOLUME_PERCENT_DOSE_ROI``
  * Arguments: Volume (%) of the *roi_name* covered by *arg_1*

* Volume (cc) of the specified structure in specified dose range (Gy)

  * Type: ``VOLUME_CC_DOSE_RANGE_ROI``
  * Arguments: Volume (cc) of the *roi_name* in range of *arg_1* to *arg_2* (Gy)

* Volume (%) of the specified structure in specified dose range (Gy)

  * Type: ``VOLUME_PERCENT_DOSE_RANGE_ROI``
  * Arguments: Volume (%) of the *roi_name* in range of *arg_1* to *arg_2* (Gy)

* Minimum dose (Gy) to the specified structure

  * Type: ``MIN_DOSE_ROI``
  * Arguments: Minimum dose (Gy) to the *roi_name*

* Maximum dose (Gy) to the specified structure

  * Type: ``MAX_DOSE_ROI``
  * Arguments: Maximum dose (Gy) to the *roi_name*

* Mean dose (Gy) to the specified structure

  * Type: ``MEAN_DOSE_ROI``
  * Arguments: Mean dose (Gy) to the *roi_name*

* Integral dose (Gy |middot| cc) to the specified structure

  * Type: ``INTEGRAL_DOSE_ROI``
  * Arguments: Integral dose (Gy |middot| cc) to the *roi_name*

* Global maximum dose (Gy) over the entire dose grid

  * Type: ``MAX_DOSE``
  * Arguments: Global maximum dose (Gy) over the entire dose grid

* Volume of Regret

  * Type: ``VOLUME_OF_REGRET``
  * Arguments: Total volume (cc) covered by *arg_1* (Gy) but outside of the *roi_name*

* Irradiated Volume

  * Type: ``IRRADIATED_VOLUME``
  * Arguments: Total volume (cc) covered by *arg_1*

* Conformation Number

  * Type: ``CONFORMATION_NUMBER``
  * Arguments: Conformation number of *roi_name* at *arg_1*

* Conformality Index

  * Type: ``CONFORMALITY_INDEX``
  * Arguments: Conformality index of *roi_name* at *arg_1*

* Homogeneity Index

  * Type: ``HOMOGENEITY_INDEX``
  * Arguments: Homogeneity index of *roi_name* at *arg_1*

* Inhomogeneity Index

  * Type: ``INHOMOGENEITY_INDEX``
  * Arguments: Inhomogeneity index of *roi_name*

* Cumulative meterset for all associated treatment beams

  * Type: ``CUMULATIVE_METERSET``
  * Arguments: Cumulative meterset

* Volume (cc) of the specified structure

  * Type: ``VOLUME``
  * Arguments: Volume (cc) of the *roi_name*
