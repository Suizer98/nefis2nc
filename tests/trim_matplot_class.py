# Setup geotiff file name to work with geoserver image mosaic time series
import datetime
import xarray as xr
import numpy as np
from shapely.geometry import Polygon
from osgeo import ogr, gdal, osr
import os
from datetime import timedelta
import pandas as pd

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#################### Multiprocessing module ####################
# import multiprocess as mp


class trimFile:
    """Loads data from a netcdf file that was converted from a NEFIS trim file."""

    def __init__(self, trim_in, geotiff_folder_out):
        self.trim_in = trim_in
        self.geotiff_folder_out = geotiff_folder_out

    def hour_rounder(self, t):
        # Rounds to nearest hour by adding a timedelta hour if minute >= 30
        return t.replace(second=0, microsecond=0, minute=0, hour=t.hour) + timedelta(
            hours=t.minute // 30
        )

    def worker(self, t, timestamp, corners_1d, water_level_1d, geotiff_folder_out):
        time_lap = datetime.datetime.now()
        driver = ogr.GetDriverByName("Esri Shapefile")
        dest_srs = osr.SpatialReference()
        dest_srs.ImportFromEPSG(4326)
        data_source_file = "{}/nc_to_polygons_v5_{}.shp".format(geotiff_folder_out, t)
        shp_out = driver.CreateDataSource(data_source_file)
        layer = shp_out.CreateLayer("", dest_srs, ogr.wkbPolygon)
        # Add one attribute
        layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("waterlevel", ogr.OFTReal))
        defn = layer.GetLayerDefn()
        id = 0
        for i in range(len(corners_1d)):
            corners = corners_1d[i]
            water_level = float(water_level_1d[i][t])
            has_masked = any(np.ma.is_masked(val) for point in corners for val in point)
            if has_masked:
                # At least one value in the corners list is masked
                continue  # Skip the current iteration and move to the next one

            poly = Polygon(corners)  #
            feat = ogr.Feature(defn)
            feat.SetField("id", int(id))
            feat.SetField("waterlevel", water_level)  #

            geom = ogr.CreateGeometryFromWkb(poly.wkb)
            feat.SetGeometry(geom)
            layer.CreateFeature(feat)
            feat = geom = None  # destroy these
            id += 1

        # gdal
        # src_layer = layer.GetLayer()
        pixels = 2000
        # source_ds = ogr.Open('my.shp')
        source_layer = shp_out.GetLayer()
        x_min, x_max, y_min, y_max = source_layer.GetExtent()
        x_pixel_size = float((x_max - x_min) / pixels)
        y_pixel_size = float((y_max - y_min) / pixels)
        driver2 = gdal.GetDriverByName("GTiff")

        # time_parsed = datetime.strptime(timestamp[:-10],"%Y-%m-%dT%H:%M:%S")
        raster_output_file = os.path.join(
            geotiff_folder_out,
            "waterlevel_{}.tif".format(timestamp.strftime("%Y%m%d%H")),
        )

        dst_ds = driver2.Create(raster_output_file, pixels, pixels, 1, gdal.GDT_Float32)

        out_lyr = dst_ds.GetRasterBand(1)
        out_lyr.SetNoDataValue(-9999)
        dst_ds.SetGeoTransform((x_min, x_pixel_size, 0, y_max, 0, -y_pixel_size))

        # assign crs to raster
        dest_srs = osr.SpatialReference()
        dest_srs.ImportFromEPSG(4326)
        dst_ds.SetSpatialRef(dest_srs)

        gdal.RasterizeLayer(dst_ds, [1], source_layer, options=["ATTRIBUTE=waterlevel"])

        # Delete shapefile
        shp_out.Destroy()
        driver.DeleteDataSource(data_source_file)

        time_taken = datetime.datetime.now() - time_lap
        print("%s took %s" % (t, time_taken))

    ################################################################

    def trimnc2geotiffolder(self):
        try:
            # try to initialise geotiff folder
            os.mkdir(self.geotiff_folder_out)
        except Exception:
            pass
        ds = xr.open_dataset(self.trim_in, drop_variables="time_bounds")
        time = ds.time
        m = len(ds.m)
        n = len(ds.n)
        # i = 0

        begin_time = datetime.datetime.now()

        # copy out grid arrays for efficiency
        lat_array = ds.latitude.to_masked_array()
        lon_array = ds.longitude.to_masked_array()
        grid_longitude_array = ds.grid_longitude.to_masked_array()
        grid_latitude_array = ds.grid_latitude.to_masked_array()
        water_level_array = ds.waterlevel.to_masked_array()
        time_array = ds.time.to_masked_array()

        # data_array = ds.grid_longitude[:, :, 0].values
        # df = pd.DataFrame(data_array)
        # df.to_csv('grid_longitudeori1.csv')
        # data_array = ds.grid_longitude[:, :, 1].values
        # df = pd.DataFrame(data_array)
        # df.to_csv('grid_longitudeori2.csv')
        # data_array = ds.grid_longitude[:, :, 2].values
        # df = pd.DataFrame(data_array)
        # df.to_csv('grid_longitudeori3.csv')
        # data_array = ds.grid_longitude[:, :, 3].values
        # df = pd.DataFrame(data_array)
        # df.to_csv('grid_longitudeori4.csv')

        # data_array = ds.grid_longitude[:, :, 0].values
        # df = pd.DataFrame(data_array)
        # df.to_csv("grid_longitudenew1.csv")
        # data_array = ds.grid_longitude[:, :, 1].values
        # df = pd.DataFrame(data_array)
        # df.to_csv("grid_longitudenew2.csv")
        # data_array = ds.grid_longitude[:, :, 2].values
        # df = pd.DataFrame(data_array)
        # df.to_csv("grid_longitudenew3.csv")
        # data_array = ds.grid_longitude[:, :, 3].values
        # df = pd.DataFrame(data_array)
        # df.to_csv("grid_longitudenew4.csv")
        # return

        # flatten to 1dimension and remove nan cells
        # get grid
        corners_1d = []
        lat_1d = []
        lon_1d = []
        grid_longitude_1d = []
        grid_latitude_1d = []
        water_level_1d = []
        for x in range(1, m):
            for y in range(1, n):
                if np.isnan(float(lat_array[x][y])):
                    # nan cells have nan for all fields, skip those to improve efficiency
                    continue
                lat_1d.append(lat_array[x][y])
                lon_1d.append(lon_array[x][y])
                grid_longitude = grid_longitude_array[x][y]  #
                grid_longitude_1d.append(grid_longitude)
                grid_latitude = grid_latitude_array[x][y]  #
                grid_latitude_1d.append(grid_latitude)
                corners = zip(grid_longitude, grid_latitude)  #
                corners_1d.append(list(corners))
                water_level_1d.append(water_level_array[:, x, y])

        print(np.array(water_level_1d).shape)
        print("initialised grid")
        print(datetime.datetime.now() - begin_time)  # 4s

        for t in range(len(time_array)):
            time_dt_64 = time_array[t]
            time_dt = datetime.datetime.utcfromtimestamp(time_dt_64.item() / 1e9)
            time_dt_rounded = self.hour_rounder(time_dt)
            self.worker(
                t, time_dt_rounded, corners_1d, water_level_1d, self.geotiff_folder_out
            )

        print(datetime.datetime.now() - begin_time)

    def plotAnimation(self, mp4VideoOut=None):
        # list all the tiff files in the directory
        folder = os.path.join(self.geotiff_folder_out, "")
        # folder = "./trim-scsmCddbTIFF/"
        tif_files = [f for f in os.listdir(folder) if f.endswith(".tif")]

        if len(tif_files) == 0:
            print(
                "No tiff file found in folder! Use <object>.trimnc2geotifffolder to create tiff files."
            )
            return

        # create an empty list to store the data arrays
        title_list = []
        data_list = []

        # loop through each tiff file
        for filename in tif_files:
            # filename = 'waterlevel_2001122500.tif'
            print("Processing file {}".format(filename))
            title_list.append(filename)

            dataset = gdal.Open(folder + filename, gdal.GA_ReadOnly)
            # print(dataset.RasterCount, dataset.RasterXSize, dataset.RasterYSize)

            # get the geotransform information
            geotransform = dataset.GetGeoTransform()

            # check if pixel size or y-coordinate needs to be flipped
            if geotransform[1] < 0:
                geotransform = list(geotransform)
                geotransform[1] *= -1
                geotransform = tuple(geotransform)
            if geotransform[5] > 0:
                geotransform = list(geotransform)
                geotransform[3] += dataset.RasterYSize * geotransform[5]
                geotransform[5] *= -1
                geotransform = tuple(geotransform)

            # Note GetRasterBand() takes band no. starting from 1 not 0
            band1 = dataset.GetRasterBand(1)
            arr = band1.ReadAsArray()

            # create a masked array to mask the -9999 values
            masked_arr = np.ma.masked_where(arr == -9999, arr)

            # create an array of raster coordinates
            y, x = np.meshgrid(
                np.arange(dataset.RasterYSize), np.arange(dataset.RasterXSize)
            )

            # convert raster coordinates to latitudes and longitudes
            lon = geotransform[0] + x * geotransform[1] + y * geotransform[2]
            lat = geotransform[3] + x * geotransform[4] + y * geotransform[5]

            # add the masked array to the list
            data_list.append(masked_arr)

            # close the dataset
            dataset = None

        # create a figure and axis
        fig, ax = plt.subplots()

        # create the initial image
        im = ax.imshow(
            data_list[0],
            cmap="Blues",
            extent=[lon.min(), lon.max(), lat.min(), lat.max()],
        )

        # set the title of the initial image
        ax.set_title(title_list[0])

        # function to update the image
        def update(i):
            # update the image data
            im.set_data(data_list[i])

            # set the title of the image
            ax.set_title(title_list[i])

            # return the image
            return (im,)

        # create the animation
        ani = FuncAnimation(fig, update, frames=len(data_list), interval=1000)

        # show the animation
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.show()

        # save mp4, if error codes happened, ffmpeg is needed on local machine
        # https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/
        # https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/
        # matplotlib.rcParams['animation.ffmpeg_path'] = "C:\\Users\\CodersLegacy\\Desktop\\ffmpeg-5.0.1-essentials_build\\bin\\ffmpeg.exe"
        # f = "scsmCddb_waterlevels.mp4"
        # writermp4 = FFMpegWriter(fps=20)
        # ani.save(f, writer=writermp4)

        # save mp4 without ffmpeg
        if mp4VideoOut:
            print("Processing mp4 output...")
            ani.save(mp4VideoOut)
        else:
            pass


testDirectory = os.path.join(os.getcwd(), "tests/testdata/")
# gg = trimFile(
#     testDirectory + "trim-scsmCddb.nc",
#     testDirectory + "testori",
# )
# a = gg.trimnc2geotiffolder()
# gg.plotAnimation("scsmCddb_waterlevels_ori.mp4")
gg2 = trimFile(
    testDirectory + "output-trim-final.nc",
    testDirectory + "test",
)
b = gg2.trimnc2geotiffolder()
# gg2.plotAnimation("scsmCddb_waterlevels.mp4")
