import osrm  # https://github.com/ustroetz/python-osrm
import numpy as np
import pickle
import matplotlib.pyplot as plt
import folium
from mpl_toolkits.basemap import Basemap  # Used to check if coordinate is land (pip install basemap-data-hires)
from util import flat2lla
from datetime import datetime


class TravelTime:
    def __init__(self, destination_latitude_deg, destination_longitude_deg):
        self.destination_coordinates_long_lat_deg = [destination_longitude_deg, destination_latitude_deg]

        # Define default square grid size of 30 km around the destination coordinates
        self._east_west_grid_size_km = 30
        self._north_south_grid_size_km = 30
        self._resolution_km = 10
        self._number_of_grid_points = 0

        self._latitude_departure_deg = None
        self._longitude_departure_deg = None
        self._travel_time_sec = None

        # Initialize a default grid
        self.__generate_grid()

    # Declaring private method
    def __generate_grid(self):
        """
        __generate_grid generates a square grid with latitudes and longitudes around the destination coordinates
        :param: none
        :return: none
        """

        # Compute a square grid around the destination
        x = np.arange(-self._east_west_grid_size_km, self._east_west_grid_size_km + 1, self._resolution_km) * 1000
        y = np.arange(-self._north_south_grid_size_km, self._north_south_grid_size_km + 1, self._resolution_km) * 1000

        # Generate a meshgrid
        xx, yy = np.meshgrid(x, y)

        # Flatten the arrays
        xx = xx.flatten()
        yy = yy.flatten()

        # Converting the x-, y-coordinates to latitude and longitude
        self._longitude_departure_deg, \
            self._latitude_departure_deg = flat2lla(xx, yy,
                                                    self.destination_coordinates_long_lat_deg[0],
                                                    self.destination_coordinates_long_lat_deg[1])
        self._number_of_grid_points = len(xx)

    def set_grid(self, east_west_grid_size_km, north_south_grid_size_km, resolution_km):
        """
        set_grid generates a square grid with latitudes and longitudes around the destination coordinates. The input
        is based on east-west, north-south square with a resolution, all defined in kilometers
        :param east_west_grid_size_km : width of the grid in east-west direction in km
        :param north_south_grid_size_km : width of the grid in north-south direction in km
        :param resolution_km: resolution of the grid in km
        :param
        :return: none
        """

        self._east_west_grid_size_km = east_west_grid_size_km
        self._north_south_grid_size_km = north_south_grid_size_km
        self._resolution_km = resolution_km

        # create the new grid
        self.__generate_grid()

    def retrieve_travel_times(self):
        """
        retrieve_travel_times request the travel times using the Open Source Routing Machine (OSRM). This function
        requires a connection towards an OSRM server, which can be either hosted locally or used online. For now this
        function requires an internet connection to connect with router.project-osrm.org

        :param: none
        :return: numpy array containing latitude, longitude and travel time (3xN)
        """
        # Departure coordinates are longitude and latitude
        departure_coordinates = [[float(lon), float(lat)] for lon, lat in
                                 zip(self._longitude_departure_deg, self._latitude_departure_deg)]

        # Initialize empty array
        self._travel_time_sec = np.empty((0, 0))

        # Define the host for requesting open source routing machine (OSRM)
        osrm.RequestConfig.host = "router.project-osrm.org"
        number_of_maximum_requested_coordinates = 150  # Using more than 150 request at a time results in an error.
        # (TODO: This also seems to depend on distance between coordinates)

        # If number of coordinates in the grid is smaller than maximum coordinates that can be requested, just limit
        # the number of requested coordinates
        if len(departure_coordinates) < number_of_maximum_requested_coordinates:
            number_of_maximum_requested_coordinates = len(departure_coordinates)

        idx = 0
        # Start requesting travel times for the coordinates defined in the grid
        while idx < len(departure_coordinates):
            then = datetime.now()
            time_matrix = osrm.table(departure_coordinates[idx:idx + number_of_maximum_requested_coordinates],
                                     coords_dest=[self.destination_coordinates_long_lat_deg],
                                     send_as_polyline=False)

            self._travel_time_sec = np.append(self._travel_time_sec, time_matrix[0])
            idx = idx + number_of_maximum_requested_coordinates

            # Make sure we never request more coordinates than available in the grid
            if idx > len(departure_coordinates):
                idx = len(departure_coordinates)

            now = datetime.now()  # Now
            duration = now - then  # For build-in functions
            duration_in_s = duration.total_seconds()  # Total number of seconds between dates
            print('Number of coordinates processed: ' + str(idx) + '/' + str(self._number_of_grid_points)
                  + ' (Duration: ' + str(duration_in_s) + ' s)')

        # Create a basemap to identify if the coordinate is land or water
        hires_base_map = Basemap(
            area_thresh=10,
            resolution="h",
            llcrnrlon=min(self._longitude_departure_deg - 1.0),  # Lower left corner longitude
            llcrnrlat=min(self._latitude_departure_deg - 1.0),  # Lower left corner latitude
            urcrnrlon=max(self._longitude_departure_deg + 1.0),  # Upper Right corner longitude
            urcrnrlat=max(self._latitude_departure_deg + 1.0)  # Upper Right corner latitude
        )

        # Check if coordinate is in the water, if so set travel time to -100, since negative values are impossible
        for i in range(len(self._travel_time_sec)):
            if not hires_base_map.is_land(self._longitude_departure_deg[i], self._latitude_departure_deg[i]):
                self._travel_time_sec[i] = -100

        # Return data as a 3xN array with latitude, longitude and travel time
        return np.stack((self._latitude_departure_deg,
                         self._longitude_departure_deg,
                         self._travel_time_sec))

    def save_data_to_pkl(self, filename):
        """
        save_data_to_pkl saves the latitude, longitude and travel time in a pickle file

        :param filename: give the filename
        :return: none
        """
        filename = filename + '.pckl'

        file = open(filename, 'wb')
        pickle.dump([self._latitude_departure_deg, self._longitude_departure_deg, self._travel_time_sec], file)
        file.close()

    def create_folium_map(self, filename):
        """
        create_folium_map creates a folium map with the travel times (in minutes) plotted on top of it. An internet
        connection is required for the usage of folium

        :param filename: give the filename to store the folium map as html
        :return: none
        """
        filename = filename + '.html'

        # Start a figure
        fig = plt.figure()

        # Create a contour plt
        cs = plt.tricontourf(self._longitude_departure_deg, self._latitude_departure_deg, self._travel_time_sec/60,
                             levels=[-50, 0, 10, 20, 30, 40, 50, 60],
                             cmap=plt.cm.jet)

        # Create legend
        proxy = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in cs.collections]
        plt.legend(proxy, ['water', 0, 10, 20, 30, 40, 50, 60], prop={'size': 6},
                   loc='upper right')

        # Clean up figure
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())

        # "Draw" the figure first
        fig.canvas.draw()

        # Save it to a numpy array.
        image_data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image_data = image_data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        # Create a folium map
        map_osm = folium.Map(location=[self.destination_coordinates_long_lat_deg[1],
                                       self.destination_coordinates_long_lat_deg[0]], zoom_start=10)

        # Add destination location
        folium.Marker([self.destination_coordinates_long_lat_deg[1],
                       self.destination_coordinates_long_lat_deg[0]], popup='Work').add_to(map_osm)

        # Add contour data on top of folium map
        folium.raster_layers.ImageOverlay(
            image=image_data,
            bounds=[[min(self._latitude_departure_deg), min(self._longitude_departure_deg)],
                    [max(self._latitude_departure_deg), max(self._longitude_departure_deg)]],
            opacity=0.4,
        ).add_to(map_osm)

        # Save to .html file
        map_osm.save(filename)
