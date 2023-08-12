from stompy.model.delft.nefis import Nefis
from stompy.model.delft.nefis_nc import nefis_to_nc
import netCDF4
import numpy as np
import os
from datetime import datetime, timedelta


def char_array_2_string(char_array):
    """
    Strings in NetCDF (Network Common Data Form) files are typically stored in binary form.
    In case you want to extract Station names from netcdf file, this can come to handy.
    """
    # initialization of string to ""
    new = ""

    # traverse in the string
    for x in char_array:
        new += x.decode("utf-8")

        # return string
    return new


def convert_time_step(ITDATE, tunit, dt, itmapc):
    """
    In original trih.nc file, the time intervals stored in the unit of days.
    We should do that in here too.
    The logic here is:
    ITDATE + first row of ithisc = Model start date
    ITDATE + last row of ithisc = Model end date
    """

    # Given data
    ITDATE = ITDATE
    tunit = tunit
    dt = dt
    itmapc = np.array(itmapc)

    # Calculate the time step in seconds
    time_step_seconds = tunit * dt

    # Convert ITDATE to a datetime object
    ITDATE_date = datetime.strptime(str(ITDATE), "%Y%m%d")

    # Convert ithisc to actual dates
    actual_dates = []
    for step in itmapc:
        # Calculate the time delta in seconds, days, hours etc.
        time_delta_seconds = step * time_step_seconds

        days = time_delta_seconds // (24 * 3600)
        remaining_seconds = time_delta_seconds % (24 * 3600)

        hours = remaining_seconds // 3600
        remaining_seconds %= 3600

        minutes = remaining_seconds // 60
        remaining_seconds %= 60

        seconds = remaining_seconds
        microseconds = remaining_seconds * 1e6

        # Create the timedelta object
        time_delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
        )

        # Calculate the actual date
        actual_date = ITDATE_date + time_delta
        actual_dates.append(actual_date)

    # Print the results
    date_list = []
    day_list = []
    for step, date in zip(itmapc, actual_dates):
        formatted_date = date.strftime("%Y-%m-%dT%H:%M:%S")
        reference_date = "1970-01-01T00:00:00"
        formatted_datetime = datetime.strptime(formatted_date, "%Y-%m-%dT%H:%M:%S")
        reference_datetime = datetime.strptime(reference_date, "%Y-%m-%dT%H:%M:%S")
        time_difference_seconds = (
            formatted_datetime - reference_datetime
        ).total_seconds()
        difference_in_days = time_difference_seconds / (24 * 3600)

        # date_list = ['1970-01-01T00:00:00', ...]
        date_list.append("{}".format(formatted_date))
        # day_list = [11097, ...]
        day_list.append(difference_in_days)

    return day_list


def create_raw_nc(datfile, deffile, outputfile):
    """
    This function create netcdf file as close as to its raw form.
    The variables & dimensions naming are all directly borrowed from Nefis.
    """

    # Create nc object dataset
    nefisObject = Nefis(datfile, deffile)
    nc = nefis_to_nc(nefisObject)

    # Create a new NetCDF file
    output_file = outputfile
    dataset = netCDF4.Dataset(output_file, "w", format="NETCDF4")

    # Add dimensions to the dataset
    for dim_name, dim in nc.dimensions.items():
        dataset.createDimension(dim_name, len(dim))

    # Add variables to the dataset
    for var_name, var in nc.variables.items():
        # Create the variable in the dataset with the same name and data type
        dims = [dim_name for dim_name in var.dimensions]
        dataset.createVariable(var_name, var.dtype, dims)
        # Assign the variable's values from the original dataset
        dataset.variables[var_name][:] = var[:]

    # Close the dataset to ensure the file is saved
    dataset.close()
    print("NetCDF file has been created.")


def create_organised_trimnc(datfile, deffile, outputfile):
    """
    This function create netcdf file as close as to vs_trim2nc.m product.
    The variables & dimensions naming referred to what described in vs_trim2nc.m.
    """

    # Create nc object dataset
    nefisObject = Nefis(datfile, deffile)
    src_ds = nefis_to_nc(nefisObject)

    # Create a new NetCDF file
    output_file = outputfile
    dst_ds = netCDF4.Dataset(output_file, "w", format="NETCDF4")

    # Access the 'time' variableg
    ITDATE = src_ds.variables["itdate"][0]
    tunit = src_ds.variables["tunit"][0]
    dt = src_ds.variables["dt"][0]
    itmapc = src_ds.variables["itmapc"][:]
    time = convert_time_step(ITDATE, tunit, dt, itmapc)

    # Access the 'waterlevel' variable
    waterlevel = src_ds.variables["s1"]
    masked_waterlevel = np.ma.masked_equal(waterlevel, 0)
    masked_waterlevel = masked_waterlevel.filled(np.nan)

    # Access the 'mn' variable
    nmax = src_ds.variables["nmax"][:]
    mmax = src_ds.variables["mmax"][:]
    ndata = np.arange(1, nmax + 1).reshape(-1, 1)
    mdata = np.arange(1, mmax + 1).reshape(-1, 1)

    # Access the 'grid_xy' variable
    xcor = src_ds.variables["xcor"]
    ycor = src_ds.variables["ycor"]
    # Apply mask
    kcs = src_ds.variables["kcs"][:]
    kcs = kcs.astype(float)
    kcs[(kcs == 3) & (kcs == 2) & (kcs == 1) ] = 1
    kcs[(kcs != 1) & (kcs != 0) ] = 0
    xcor = kcs * xcor
    ycor = kcs * ycor
    masked_xcor = np.ma.masked_equal(xcor, 0)
    masked_ycor = np.ma.masked_equal(ycor, 0)
    masked_ycor = masked_ycor.filled(np.nan)
    masked_xcor = masked_xcor.filled(np.nan)

    # Access the 'xy' variable, we need to apply mask from 'kcs'
    xzdata = src_ds.variables["xz"]
    yzdata = src_ds.variables["yz"]
    # Apply mask
    kcs = src_ds.variables["kcs"][:]
    kcs = kcs.astype(float)
    kcs[(kcs == 3) & (kcs == 2) & (kcs == 1) ] = 1
    kcs[(kcs != 1) & (kcs != 0)] = 0
    longitude = kcs * xzdata
    latitude = kcs * yzdata
    masked_latitude = np.ma.masked_equal(latitude, 0)
    masked_longitude = np.ma.masked_equal(longitude, 0)
    masked_latitude = masked_latitude.filled(np.nan)
    masked_longitude = masked_longitude.filled(np.nan)

    # Perform the shift
    # def rollrep(arr):
    #     arr = np.roll(arr, axis=0, shift=1)
    #     arr[0, :] = 0
    #     return arr
    #
    # longitude = rollrep(longitude)
    # latitude = rollrep(latitude)

    # Add dimensions to the dataset
    dst_ds.createDimension("time", len(time))
    dst_ds.createDimension("n", src_ds.variables["nmax"][:])
    dst_ds.createDimension("m", src_ds.variables["mmax"][:])
    dst_ds.createDimension("k", src_ds.variables["kmax"][:])
    dst_ds.createDimension("Layer", src_ds.variables["kmax"][:])
    dst_ds.createDimension("LayerInterf", src_ds.variables["kmax"][:] + 1)
    dst_ds.createDimension("bounds2", 2)
    dst_ds.createDimension("bounds4", 4)

    # Add the "time" variable to the destination dataset
    dst_var_time = dst_ds.createVariable("time", "f8", ("time",))  # Use 'f8' for float64 data type
    dst_var_time[:] = time
    dst_var_time.units = "days since 1970-01-01"
    dst_var_time.calendar = "standard"

    # Add mn variable
    m = dst_ds.createVariable("m", "int", ("m"))
    n = dst_ds.createVariable("n", "int", ("n"))
    m[:] = mdata
    n[:] = ndata

    # Add grid_latitude and grid_longitude variable
    grid_latitude = dst_ds.createVariable("grid_latitude", float, ("m", "n", "bounds4"))
    grid_longitude = dst_ds.createVariable("grid_longitude", float, ("m", "n", "bounds4"))

    # Create four redundant sets of grid_latitude and grid_longitude
    for i in range(4):
        if i == 0:
            # Create the shifted arrays
            shifted_xcor = np.roll(masked_xcor, 1, axis=0)
            shifted_xcor = np.roll(shifted_xcor, 1, axis=1)
            shifted_ycor = np.roll(masked_ycor, 1, axis=0)
            shifted_ycor = np.roll(shifted_ycor, 1, axis=1)
            grid_longitude[:, :, i] = shifted_xcor
            grid_latitude[:, :, i] = shifted_ycor
        if i == 1:
            # Create the shifted arrays
            shifted_xcor = np.roll(masked_xcor, 1, axis=0)
            shifted_ycor = np.roll(masked_ycor, 1, axis=0)
            grid_longitude[:, :, i] = shifted_xcor
            grid_latitude[:, :, i] = shifted_ycor
        if i == 2:
            # Create the shifted arrays
            grid_longitude[:, :, i] = masked_xcor
            grid_latitude[:, :, i] = masked_ycor
        if i == 3:
            # Create the shifted arrays
            shifted_xcor = np.roll(masked_xcor, 1, axis=1)
            shifted_ycor = np.roll(masked_ycor, 1, axis=1)
            grid_longitude[:, :, i] = shifted_xcor
            grid_latitude[:, :, i] = shifted_ycor


    # Add latitude and longitude variable
    lat_var = dst_ds.createVariable("latitude", float, ("m", "n"))
    lon_var = dst_ds.createVariable("longitude", float, ("m", "n"))
    lat_var[:] = masked_latitude
    lon_var[:] = masked_longitude

    # Add waterlevel variable
    waterlevel_var = dst_ds.createVariable("waterlevel", "float", ("time", "m", "n"))
    waterlevel_var[:] = masked_waterlevel

    variables = [
        {
            "name": "u1",
            "dimensions": ["time", "n", "m", "k"],
            "dtype": "float",
            "standard_name": "eastward_sea_velocity",
        },
        # {
        #     "name": "s1",
        #     "dimensions": ["time", "n", "m", "k"],
        #     "dtype": "float",
        #     "standard_name": "water_level_data",
        # },
        # {
        #     "name": "itmapc",
        #     "dimensions": ["time"],
        #     "dtype": "float",
        #     "standard_name": "time"
        # },
    ]

    # for name, var in variables:
    #     if name != 'u1':
    #         dst_ds.createVariable

    # Use the variables passed as an argument
    if variables is not None:
        for var in variables:
            name = var["name"]
            dims = var["dimensions"]
            dtype = var["dtype"]
            standard_name = var["standard_name"]

            # Create the variable in the destination dataset
            dst_var = dst_ds.createVariable(name, dtype, dims)

            # Set the standard_name attribute
            if standard_name is not None:
                dst_var.setncattr("standard_name", standard_name)

            # Assign the variable's values from the original dataset
            dst_var[:] = src_ds.variables[name][:]

    src_ds.close()
    dst_ds.close()
    print("NetCDF file has been created.")


testDirectory = os.path.join(os.getcwd(), "testdata/")
# gg1 = create_raw_nc(
#     testDirectory + "trim-scsmCddb.dat",
#     testDirectory + "trim-scsmCddb.def",
#     testDirectory + "output-trim.nc"
# )
gg = create_organised_trimnc(
    testDirectory + "trim-scsmCddb.dat",
    testDirectory + "trim-scsmCddb.def",
    testDirectory + "output-trim-final.nc",
)
