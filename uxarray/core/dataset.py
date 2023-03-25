import numpy as np
import xarray as xr

import sys

from collections.abc import Hashable

from typing import Optional, IO

from uxarray.core.dataarray import UxDataArray
from uxarray.core.grid import Grid


class UxDataset(xr.Dataset):

    # expected instance attributes, required for subclassing with xarray (as of v0.13.0)
    __slots__ = (
        '_uxgrid',
        'source_datasets',
    )

    def __init__(self,
                 *args,
                 uxgrid: Grid = None,
                 source_datasets: Optional[str] = None,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self._uxgrid = uxgrid
        setattr(self, 'source_datasets', source_datasets)

        if uxgrid is None or not isinstance(uxgrid, Grid):
            raise RuntimeError(
                "uxgrid cannot be None or it needs to "
                "be of an instance of the uxarray.core.Grid class")
        else:
            self.uxgrid = uxgrid

    @property
    def uxgrid(self):
        return self._uxgrid

    # a setter function
    @uxgrid.setter
    def uxgrid(self, ugrid):
        self._uxgrid = ugrid

    def _construct_dataarray(self, name) -> UxDataArray:
        """Override to check if the result is an instance of xarray.DataArray.

        If so, convert to UxDataArray.
        """
        xarr = super()._construct_dataarray(name)
        return UxDataArray(xarr, uxgrid=self.uxgrid)

    def __getitem__(self, key):
        """Override to check if the result is an instance of xarray.DataArray.

        If so, convert to UxDataArray.
        """
        xarr = super().__getitem__(key)

        if isinstance(xarr, xr.DataArray):
            return UxDataArray(xarr, uxgrid=self.uxgrid)
        else:
            assert isinstance(xarr, xr.Dataset)
            return UxDataset(xarr, uxgrid=self.uxgrid)

    def __setitem__(self, key, value):
        """Override to check if the value being set is an instance of
        xarray.DataArray.

        If so, convert to UxDataArray.
        """
        if isinstance(value, xr.DataArray):
            value = UxDataArray(value)
            # works with the value below also.
            # value = value.to_dataarray()

        super().__setitem__(key, value)

    @classmethod
    def from_dataframe(cls, dataframe):
        """Convert to a UxDataset instead of an xarray.Dataset."""
        return cls(
            {
                col: ('index', dataframe[col].values)
                for col in dataframe.columns
            },
            coords={'index': dataframe.index})

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Convert to a UxDataset instead of an xarray.Dataset."""
        return cls({key: ('index', val) for key, val in data.items()},
                   coords={'index': range(len(next(iter(data.values()))))},
                   **kwargs)

    def info(self, buf: IO = None, show_attrs=False) -> None:
        """
        Concise summary of a Dataset variables and attributes including
        grid topology information stored in the (``uxgrid``) accessor
        Parameters
        ----------
        buf : file-like, default: sys.stdout
            writable buffer
        show_attrs : bool
            Flag to select whether to show attributes
        See Also
        --------
        pandas.DataFrame.assign
        ncdump : netCDF's ncdump
        """
        if buf is None:  # pragma: no cover
            buf = sys.stdout

        lines = []
        lines.append("uxarray.Dataset {")

        lines.append("grid topology dimensions:")
        for name, size in self.uxgrid._ds.dims.items():
            lines.append(f"\t{name} = {size}")

        lines.append("\ngrid topology variables:")
        for name, da in self.uxgrid._ds.variables.items():
            dims = ", ".join(map(str, da.dims))
            lines.append(f"\t{da.dtype} {name}({dims})")
            if show_attrs:
                for k, v in da.attrs.items():
                    lines.append(f"\t\t{name}:{k} = {v}")

        lines.append("\ndata dimensions:")
        for name, size in self.dims.items():
            lines.append(f"\t{name} = {size}")

        lines.append("\ndata variables:")
        for name, da in self.variables.items():
            dims = ", ".join(map(str, da.dims))
            lines.append(f"\t{da.dtype} {name}({dims})")
            if show_attrs:
                for k, v in da.attrs.items():
                    lines.append(f"\t\t{name}:{k} = {v}")

        if show_attrs:
            lines.append("\nglobal attributes:")
            for k, v in self.attrs.items():
                lines.append(f"\t:{k} = {v}")

        lines.append("}")
        buf.write("\n".join(lines))

    # You can add custom methods to the class here
    def custom_method(self):
        print("Custom method for the class")

    def integrate(self, quadrature_rule="triangular", order=4):
        """Integrates over all the faces of the given mesh.

        Parameters
        ----------
        quadrature_rule : str, optional
            Quadrature rule to use. Defaults to "triangular".
        order : int, optional
            Order of quadrature rule. Defaults to 4.

        Returns
        -------
        Calculated integral : float

        Examples
        --------
        Open a Uxarray dataset

        >>> import uxarray as ux
        >>> uxds = ux.open_dataset("grid.ug", "centroid_pressure_data_ug")

        # Compute the integral
        >>> integral = uxds.integrate()
        """
        integral = 0.0

        # call function to get area of all the faces as a np array
        face_areas = self.uxgrid.compute_face_areas(quadrature_rule, order)

        # TODO: Fix this requirement. It should be applicable to
        # TODO: either all variables of dataset or a dataarray instead.
        var_key = list(self.keys())
        if len(var_key) > 1:
            # warning: print message
            print(
                "WARNING: The dataset has more than one variable, using the first variable for integration"
            )

        var_key = var_key[0]
        face_vals = self[var_key].to_numpy()
        integral = np.dot(face_areas, face_vals)

        return integral
