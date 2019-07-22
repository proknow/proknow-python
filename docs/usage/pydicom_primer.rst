.. _pydicom-primer:

pydicom Primer
==============

`pydicom <https://pypi.org/project/pydicom/>`_ is a python module for working with DICOM files. We provide a primer here for things we think might be particularly useful for users of the ProKnow Python SDK. We encourage you to consult the `full documentation <https://pydicom.github.io/pydicom/stable/>`_ for more in-depth coverage of the package.

Reading Files
-------------

Reading a DICOM file using ``pydicom`` is simple::

    import pydicom

    dataset = pydicom.dcmread('./plan.dcm')

Sometimes, however, you might receive an error message like this:

    pydicom.errors.InvalidDicomError: File is missing DICOM File Meta Information header or the 'DICM' prefix is missing from the header. Use force=True to force reading.

If this happens, you will have to use force=True to force pydicom to read the file.

Accessing Sequence Data
-----------------------

Let's say you wish to access the TargetPrescriptionDose located in the DoseReferenceSequence for a plan. Here's a quite example showing how this can be done::

    import pydicom

    dataset = pydicom.dcmread('./plan.dcm')

    print("Number of Items in Dose Reference Sequence:", len(dataset.DoseReferenceSequence))

    item = dataset.DoseReferenceSequence[0] # Get first item in sequence

    print("Dose Reference Type:", item.DoseReferenceType)
    print("Target Prescription Dose:", item.TargetPrescriptionDose)

Note that this example uses optional tags (DoseReferenceSequence and TargetPrescriptionDose). In your code, you should ensure that you're not attempting to access attribute values that do not exist.

Attribute Dump
--------------

If you don't know the name of the attribute you're looking for, it might be helpful to output a recursive dump of the dataset with the available attributes and values. Use the following code as a guide::

    import pydicom

    def print_dataset(dataset, depth, max_depth=None):
        for name in dataset.dir():
            value = getattr(dataset, name)
            if isinstance(value, pydicom.Sequence):
                if max_depth is not None and depth + 1 < max_depth:
                    print('{:40}  =>  ['.format(' ' * depth + name))
                    print_sequence(value, depth + 1, max_depth=max_depth)
                    print('{}]'.format(' ' * depth))
                else:
                    print('{:40}  =>  [...]'.format(' ' * depth + name))
            else:
                print('{:40}  =>  {}'.format(' ' * depth + name, value))

    def print_sequence(sequence, depth, max_depth=None):
        if max_depth is not None and depth + 1 < max_depth:
            print(' ' * depth + '{')
            for dataset in sequence:
                print_dataset(dataset, depth + 1, max_depth=max_depth)
            print(' ' * depth + '}')
        else:
            print(' ' * depth + '{...}')


    ########################################
    # Read and output root dataset

    dataset = pydicom.dcmread('./plan.dcm', force=True)
    print_dataset(dataset, 0, max_depth=1) # root dataset
    print_dataset(dataset.DoseReferenceSequence[0], 0, max_depth=1) # sequency

You can adjust ``max_depth`` up and down to control the depth of the recursion or omit it entirely for no recursion limits.
