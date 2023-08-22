from datetime import datetime, timedelta
import netCDF4 as nc
import pandas as pd
import numpy as np
import random
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class historyFile:
    """Loads data from a netcdf file that was converted from a NEFIS history file."""

    def __init__(self, file=None):
        self.file = file
        self.read_nc_file(self.file)

    def read_nc_file(self, file=None):
        trih_file = file

        if not trih_file.endswith(".nc"):
            print("Invalid nc file")
            return

        # get file
        file2read = nc.Dataset(trih_file)

        # Time component
        time = file2read.variables["time"][:]
        reference_date = "1970-01-01"
        reference_date = datetime.strptime(reference_date, "%Y-%m-%d")
        # self.time_array = [item for sublist in time for item in sublist]
        self.time_array = [
            datetime.strftime(reference_date + timedelta(days=d), "%Y-%m-%dT%H:%M:%S")
            for d in time
        ]

        # station variables
        self.stations = file2read.dimensions["Station"]
        self.platform_names = file2read.variables["platform_name"][:]
        self.water_levels = file2read.variables["waterlevel"][:]
        self.longitudes = file2read.variables["longitude"]
        self.latitudes = file2read.variables["latitude"]
        self.platform_angles = file2read.variables["platform_angle"]
        self.depths = file2read.variables["depth"]

    def plot(self, input):
        """
        Visualise trih stations
        """
        if isinstance(input, int):
            # acquire water level for one station
            water_levels_indi = []
            for i in range(len(self.water_levels)):
                water_level = self.water_levels[i]
                water_level = water_level[input]
                water_levels_indi.append(water_level)

            # data = np.array([self.time_array, water_levels_indi]).T
            # df = pd.DataFrame(data, columns=["x", "y"])
            # df.to_csv(
            #     "water level {} matplotlib.csv".format(
            #         self.char_array_2_string(self.platform_names[input])
            #     ),
            #     index=False,
            # )

            return self.time_array, water_levels_indi, self.platform_names

            # Plot
            # Generate a random color
            # r = random.random()
            # g = random.random()
            # b = random.random()
            # color = (r, g, b)
            # plt.plot(
            #     self.time_array,
            #     water_levels_indi,
            #     c=color,
            #     label=self.char_array_2_string(self.platform_names[input]),
            # )
            # plt.title(self.char_array_2_string(self.platform_names[input]))
            # plt.ylabel("Elevation (m)")
            # plt.xlabel("Time range")
            # plt.legend(loc="upper right")
            # plt.show()

        elif isinstance(input, list):
            multi_stations_list = []
            platform_names_list = []
            for s in input:
                water_levels_indi = []
                for i in range(len(self.water_levels)):
                    water_level = self.water_levels[i]
                    water_level = water_level[s]
                    water_levels_indi.append(water_level)
                multi_stations_list.append(water_levels_indi)
                platform_names_list.append(self.platform_names[s])

            # return self.time_array, multi_stations_list, platform_names_list

            for i, platform_name in enumerate(platform_names_list):
                # Generate a random color
                r = random.random()
                g = random.random()
                b = random.random()
                color = (r, g, b)
                plt.plot(
                    self.time_array,
                    multi_stations_list[i],
                    c=color,
                    label=self.char_array_2_string(platform_name),
                )

            # Plot
            plt.title(self.file)
            plt.ylabel("Elevation (m)")
            plt.xlabel("Time range")
            plt.legend(loc="upper right")
            plt.show()

        else:
            raise TypeError("station must be an integer or a list of integers")

    def char_array_2_string(self, char_array):
        # initialization of string to ""
        new = ""

        # traverse in the string
        for x in char_array:
            new += x.decode("utf-8")

            # return string
        return new


testDirectory = os.path.join(os.getcwd(), "testdata/")
# test = historyFile(testDirectory + "trih-scsmCddb.nc")
# test.plot([0, 5, 7, 200])
test = historyFile(testDirectory + "output-trih-final.nc")
test.plot([0, 5, 7, 200])
