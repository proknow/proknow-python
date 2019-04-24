.. _contouring-data:

Using Contouring Data
=====================

The first thing you'll need to do to work with contouring data is to obtain the object that holds the contours, lines, and points. The example below starts with a :class:`proknow.Patients.StructureSetItem`, finds a structure called PAROTID_LT, and gets the data for that structure::

    for roi in structure_set.rois:
        if roi.name == "PAROTID_LT":
            match = roi
            break
    else:
        match = None
    assert match is not None
    data = match.get_data()

At the end of the script above, ``data`` holds a :class:`proknow.Patients.StructureSetRoiData` object with the attributes ``contours``, ``lines``, and ``points``.

It's important to understand the structure of the contouring data from the ``contours`` attribute. ``contours`` is a list of dictionary objects, where each object contains a key-value pair for ``pos`` to denote the slice position and ``paths``, which is a list of paths. Each path is a flattened list of contour points.

In order to work with popular libraries like `pyclipper <https://pypi.org/project/pyclipper/>`_, it may be useful to convert the ``contours`` representation from ProKnow to a clipper representation. The functions below will convert transform paths from ProKnow into paths that pyclipper can use and vice versa::

    def convert_to_clipper(paths):
        cpaths = []
        for path in paths:
            cpath = []
            i = 0
            while i < len(path):
                cpath.append([path[i], path[i + 1]])
                i += 2
            cpaths.append(cpath)
        return cpaths

    def convert_to_proknow(paths):
        ppaths = []
        for path in paths:
            ppath = []
            for pair in path:
                ppath.extend(pair)
            ppaths.append(ppath)
        return ppaths

With the converted paths in hand, it should be straightforward to perform clipping operations like unions, intersections, differences, etc.
