import os
import numpy as np
import xarray as xr

from unittest import TestCase
from pathlib import Path

import uxarray as ux

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


class TestGrid(TestCase):

    def test_read_ugrid_write_exodus(self):
        """Reads a ugrid file and writes and exodus file."""

        ug_filename1 = current_path / "meshfiles" / "outCSne30.ug"
        ug_filename2 = current_path / "meshfiles" / "outRLL1deg.ug"
        ug_filename3 = current_path / "meshfiles" / "ov_RLL10deg_CSne4.ug"

        ug_outfile1 = current_path / "meshfiles" / "outCSne30.exo"
        ug_outfile2 = current_path / "meshfiles" / "outRLL1deg.g"
        ug_outfile3 = current_path / "meshfiles" / "ov_RLL10deg_CSne4.g"

        tgrid1 = ux.Grid(str(ug_filename1))
        tgrid2 = ux.Grid(str(ug_filename2))
        tgrid3 = ux.Grid(str(ug_filename3))

        tgrid1.write(str(ug_outfile1))
        tgrid2.write(str(ug_outfile2))
        tgrid3.write(str(ug_outfile3))

    def test_init_verts(self):
        """Create a uxarray grid from vertices and saves a ugrid file.

        Also, test kwargs for grid initialization
        """

        verts = np.array([[0, 0], [2, 0], [0, 2], [2, 2]])
        vgrid = ux.Grid(verts, vertices=True, islatlon=True, concave=False)

        face_filename = current_path / "meshfiles" / "1face.ug"
        vgrid.write(face_filename)

    def test_init_ds_var_methods(self):
        """Tests to see if accessing variables though set attribtues is equal
        to using the dict."""
        # Dataset with Variables in UGRID convention
        path = current_path / "meshfiles" / "outCSne30.ug"
        grid = ux.open_dataset(path)
        xr.testing.assert_equal(grid.Mesh2_node_x,
                                grid.ds[grid.ds_var_names["Mesh2_node_x"]])
        xr.testing.assert_equal(grid.Mesh2_node_y,
                                grid.ds[grid.ds_var_names["Mesh2_node_y"]])
        xr.testing.assert_equal(grid.Mesh2_face_nodes,
                                grid.ds[grid.ds_var_names["Mesh2_face_nodes"]])

        # Dataset with Variables NOT in UGRID convention
        path = current_path / "meshfiles" / "mesh.nc"
        grid = ux.open_dataset(path)
        xr.testing.assert_equal(grid.Mesh2_node_x,
                                grid.ds[grid.ds_var_names["Mesh2_node_x"]])
        xr.testing.assert_equal(grid.Mesh2_node_y,
                                grid.ds[grid.ds_var_names["Mesh2_node_y"]])
        xr.testing.assert_equal(grid.Mesh2_face_nodes,
                                grid.ds[grid.ds_var_names["Mesh2_face_nodes"]])

        # Original and Standardized Attributes
        xr.testing.assert_equal(grid.mesh_node_x, grid.Mesh2_node_x)
        xr.testing.assert_equal(grid.mesh_node_y, grid.Mesh2_node_y)
        xr.testing.assert_equal(grid.mesh_face_nodes, grid.Mesh2_face_nodes)


# TODO: Move to test_shpfile/scrip when implemented
# use external package to read?
# https://gis.stackexchange.com/questions/113799/how-to-read-a-shapefile-in-python

    def test_read_shpfile(self):
        """Reads a shape file and write ugrid file."""

        shp_filename = current_path / "meshfiles" / "grid_fire.shp"
        tgrid = ux.Grid(str(shp_filename))

    def test_read_scrip(self):
        """Reads a scrip file and write ugrid file."""

        scrip_8 = current_path / "meshfiles" / "outCSne8.nc"
        ug_30 = current_path / "meshfiles" / "outCSne30.ug"

        # Test read from scrip and from ugrid for grid class
        ux.Grid(str(scrip_8))  # tests from scrip

        ux.Grid(str(ug_30))  # tests from ugrid
