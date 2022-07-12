import os
import numpy as np
import numpy.testing as nt

from unittest import TestCase
from pathlib import Path

import uxarray as ux

try:
    import constants
except ImportError:
    from . import constants

# Data files
current_path = Path(os.path.dirname(os.path.realpath(__file__)))

exodus = current_path / "meshfiles" / "outCSne8.g"


class TestIntegrate(TestCase):

    def test_determine_file_type(self):
        """Determine if a file is of type exodus."""
        ftype = ux.determine_file_type(exodus)
        assert (ftype == "exo")

    def test_face_area_coords(self):
        """Test function for helper function get_all_face_area_from_coords."""
        # Note: currently only testing one face, but this can be used to get area of multiple faces
        x = np.array([0.57735027, 0.57735027, -0.57735027])
        y = np.array([-5.77350269e-01, 5.77350269e-01, 5.77350269e-01])
        z = np.array([-0.57735027, -0.57735027, -0.57735027])
        face_nodes = np.array([[0, 1, 2]])
        area = ux.get_all_face_area_from_coords(x,
                                                y,
                                                z,
                                                face_nodes,
                                                3,
                                                coords_type="cartesian")
        nt.assert_almost_equal(area, constants.TRI_AREA, decimal=1)

    def test_calculate_face_area(self):
        """Test function for helper function calculate_face_area - only one face."""
        # Note: currently only testing one face, but this can be used to get area of multiple faces
        # Also note, this does not need face_nodes, assumes nodes are in counterclockwise orientation
        x = np.array([0.57735027, 0.57735027, -0.57735027])
        y = np.array([-5.77350269e-01, 5.77350269e-01, 5.77350269e-01])
        z = np.array([-0.57735027, -0.57735027, -0.57735027])
        area = ux.calculate_face_area(x, y, z, "gaussian", 5, "cartesian")
        nt.assert_almost_equal(area, constants.TRI_AREA, decimal=3)
