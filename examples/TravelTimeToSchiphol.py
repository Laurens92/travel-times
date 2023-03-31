from TravelTime import TravelTime

if __name__ == "__main__":
    # Define destination location (NLR)
    destination_latitude_deg = 52.309770999286066
    destination_longitude_deg = 4.762984030674649

    # Define grid
    east_west_grid_size_km = 40
    north_south_grid_size_km = 40
    resolution_km = 1

    # Create a Travel Time object
    obj_travel_time = TravelTime(destination_latitude_deg, destination_longitude_deg)
    obj_travel_time.set_grid(east_west_grid_size_km, north_south_grid_size_km, resolution_km)
    data = obj_travel_time.retrieve_travel_times()

    # Save data to pkl such that it can be used later on
    obj_travel_time.save_data_to_pkl('TravelTime_to_Schiphol_Data')

    # Store contour information as folium map
    obj_travel_time.create_folium_map('TravelTimeMap_to_Schiphol')
