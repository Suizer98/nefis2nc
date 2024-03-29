from stompy.model.delft.nefis import Nefis
from stompy.model.delft.nefis_nc import nefis_to_nc

import netCDF4
import numpy as np
import os
import sys
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


def convert_time_step(ITDATE, tunit, dt, ithisc):
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
    ithisc = np.array(ithisc)

    # Calculate the time step in seconds
    time_step_seconds = tunit * dt

    # Convert ITDATE to a datetime object
    ITDATE_date = datetime.strptime(str(ITDATE), "%Y%m%d")

    # Convert ithisc to actual dates
    actual_dates = []
    for step in ithisc:
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
    for step, date in zip(ithisc, actual_dates):
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


def create_organised_trihnc(datfile, deffile, outputfile):
    """
    This function create netcdf file as close as to vs_trih2nc.m product.
    The variables & dimensions naming referred to what described in vs_trih2nc.m.
    """

    # Create nc object dataset
    nefisObject = Nefis(datfile, deffile)
    nc = nefis_to_nc(nefisObject)

    # Create a new NetCDF file
    output_file = outputfile
    dataset = netCDF4.Dataset(output_file, "w", format="NETCDF4")

    # Access the 'time' variable
    ITDATE = nc.variables["itdate"][0]
    tunit = nc.variables["tunit"][0]
    dt = nc.variables["dt"][0]
    ithisc = nc.variables["ithisc"][:]
    time = convert_time_step(ITDATE, tunit, dt, ithisc)

    # Access the 'xy' variable
    his_const_xystat_var = nc.variables["his-const_xystat"]
    x = his_const_xystat_var[:, 0]
    y = his_const_xystat_var[:, 1]
    longitudes = x
    latitudes = y

    # Access the 'water_level' variable
    water_levels = nc.variables["zwl"][:]

    # Access the 'depth' variable
    depths = nc.variables["his-const_dps"][:]

    # Convert platform_names to fixed-length strings
    platform_names = nc.variables["namst"][:]
    platform_names = np.array(
        [[s.encode("utf-8") for s in row] for row in platform_names]
    )

    # Access the 'platform_angle' variable
    platform_angle = nc.variables["alfas"][:]

    # Access the 'platform_m_index' and 'platform_n_index' variable
    his_const_mnstat_var = nc.variables["his-const_mnstat"]
    m = his_const_mnstat_var[:, 0]
    n = his_const_mnstat_var[:, 1]
    platform_m_index = m
    platform_n_index = n

    # todo add tau, u, mask variables
    masks = nc.variables["zkfs"][:]
    tau_x = nc.variables["ztauks"][:]
    tau_y = nc.variables["ztauet"][:]
    u_x = nc.variables["zcuru"][:]
    u_y = nc.variables["zcurv"][:]
    # u_z = nc.variables['zcurw'][:]

    # Add global attribute
    dataset.setncattr(
        "title",
        "NetCDF created from NEFIS-file {}".format(
            os.path.basename(datfile).replace("trih-", "")
        ),
    )

    # Add dimensions to the dataset
    dataset.createDimension("x", len(latitudes))
    dataset.createDimension("y", len(longitudes))
    dataset.createDimension("Station", len(platform_names))
    dataset.createDimension("name_strlen", 20)
    dataset.createDimension("time", len(time))

    # Add 'latitudes' and 'longitudes' as variables
    dataset.createVariable("longitude", x.dtype, ("x",))
    dataset.createVariable("latitude", y.dtype, ("y",))
    dataset.variables["latitude"][:] = latitudes
    dataset.variables["longitude"][:] = longitudes

    # Add 'platform_m_index' and 'platform_n_index' as variables
    dataset.createVariable("platform_m_index", x.dtype, ("x",))
    dataset.createVariable("platform_n_index", y.dtype, ("y",))
    dataset.variables["platform_m_index"][:] = platform_m_index
    dataset.variables["platform_n_index"][:] = platform_n_index

    # Define the platform_names variable as a scalar variable (no dimension)
    # dataset.createVariable('platform_name', 'S' + str(20), ('Station', 'name_strlen'))
    # for i, name in enumerate(platform_names):
    #     dataset.variables['platform_name'][i, :] = np.array(name, dtype='S' + str(20))

    platform_name_binary_var = dataset.createVariable(
        "platform_name", "S1", ("Station", "name_strlen")
    )
    platform_name_binary_var[:] = nc.variables["namst"][:]

    # Create variable for 'water_level'
    dataset.createVariable("waterlevel", float, ("time", "Station"))
    dataset.variables["waterlevel"][:] = water_levels

    # Create variable for 'depths'
    dataset.createVariable("depth", float, ("Station",))
    dataset.variables["depth"][:] = depths

    # Create variable for 'platform_angle'
    dataset.createVariable("platform_angle", float, ("Station",))
    dataset.variables["platform_angle"][:] = platform_angle

    # Create variable for 'time'
    # dataset.createVariable('time', 'S' + str(25), ('time', 'name_strlen'))
    # for i, date in enumerate(time):
    #     dataset.variables['time'][i, :] = np.array(date, dtype='S' + str(25))
    dataset.createVariable("time", float, ("time",))
    dataset.variables["time"][:] = time
    dataset.variables["time"].units = "days since 1970-01-01"
    dataset.variables["time"].calendar = "standard"

    # Create variable for tau, u, mask
    dataset.createVariable("mask", float, ("time", "Station"))
    dataset.variables["mask"][:] = masks
    dataset.createVariable("tau_x", float, ("time", "Station"))
    dataset.variables["tau_x"][:] = tau_x
    dataset.createVariable("tau_y", float, ("time", "Station"))
    dataset.variables["tau_y"][:] = tau_y
    dataset.createVariable("u_x", float, ("time", "Station"))
    dataset.variables["tau_x"][:] = u_x
    dataset.createVariable("u_y", float, ("time", "Station"))
    dataset.variables["tau_x"][:] = u_y

    # Close the dataset to ensure the file is saved
    nc.close()
    dataset.close()
    print("Trih NetCDF file has been created.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python trih2nc.py datfile deffile outputfile")
        sys.exit(1)

    datfile = sys.argv[1]
    deffile = sys.argv[2]
    outputfile = sys.argv[3]

    create_organised_trihnc(datfile, deffile, outputfile)

# testDirectory = os.path.join(os.getcwd(), "tests/testdata/")
# gg = create_organised_trihnc(
#     testDirectory + "trih-scsmCddb.dat",
#     testDirectory + "trih-scsmCddb.def",
#     testDirectory + "output-trih-final.nc",
# )
