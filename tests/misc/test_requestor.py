import pytest
import filecmp
import os

from proknow import ProKnow, Exceptions

def test_get_binary(app, entity_generator, temp_directory):
    pk = app.pk

    dose_path = os.path.abspath("./data/Becker^Matthew/HNC0522c0009_Plan1_Dose.dcm")
    dose = entity_generator(dose_path)
    
    _, content = pk.requestor.get_binary('/workspaces/' + dose.workspace_id + '/doses/' + dose.id + '/dicom')
    assert isinstance(content, bytes)
