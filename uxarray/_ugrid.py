import xarray as xr


def _read_ugrid(filepath):
    """UGRID file reader.

    Parameters: string, required
        Name of file to be read

    Returns: the xarray Dataset loaded during init.
    """

    # TODO: obtain and change to Mesh2 construct, see Issue #27
    # simply return the xarray object loaded
    
    base_dv_mt = list(
        xr.open_dataset(filepath,
                        mask_and_scale=False).filter_by_attrs(
                            cf_role="mesh_topology").keys())[0]
    
    if base_dv_mt != "Mesh2":
        # Make it Mesh2
        print("It is not Mesh2")
    else:
        print("It is Mesh2")
    # print
    return xr.open_dataset(filepath, mask_and_scale=False)


# Write a uxgrid to a file with specified format.
def _write_ugrid(ds, outfile):
    """UGRID file writer.
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset to be written to file
    outfile : string, required
        Name of output file

    Uses to_netcdf from xarray object.
    """
    print("Writing ugrid file: ", outfile)
    ds.to_netcdf(outfile)
