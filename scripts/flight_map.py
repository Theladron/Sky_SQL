from collections import Counter, defaultdict

import branca
import folium


def plot_flight_map(flight_routes, number_of_routes):
    """
    Plots the most used flight routes on a map using the given data and saves it.
    :param flight_routes: List of tuples containing flight information.
    :param number_of_routes: Number of routes shown as integer
    """
    # Count occurrences of each route
    route_counter = Counter([(r[0], r[1]) for r in flight_routes])
    top_routes = set(route for route, _ in route_counter.most_common(number_of_routes))

    # Create a dictionary to track total delay and count per airport
    airport_delays = defaultdict(lambda: {'total_delay': 0, 'count': 0, 'lat': None, 'lon': None})

    flight_map = folium.Map(location=[45.0, -98.0], zoom_start=4, tiles="OpenStreetMap")

    for route in flight_routes:
        if len(route) != 9:
            print(f"Skipping invalid entry (wrong length): {route}")
            continue

        (origin_airport,
         destination_airport,
         origin_city,
         destination_city,
         origin_lat,
         origin_lon,
         dest_lat,
         dest_lon,
         delay_percentage) = route

        # Only keep the top most used routes
        if (origin_airport, destination_airport) not in top_routes:
            continue

        try:
            origin_lat, origin_lon = float(origin_lat), float(origin_lon)
            dest_lat, dest_lon = float(dest_lat), float(dest_lon)
            delay_percentage = float(delay_percentage)
        except ValueError:
            print(f"Skipping invalid coordinates: {route}")
            continue

        # Update the total delay and count for both airports
        airport_delays[origin_airport]['total_delay'] += delay_percentage
        airport_delays[origin_airport]['count'] += 1
        airport_delays[destination_airport]['total_delay'] += delay_percentage
        airport_delays[destination_airport]['count'] += 1

        # Store the latest airport locations
        airport_delays[origin_airport]['lat'], airport_delays[origin_airport]['lon'] \
            = origin_lat, origin_lon
        airport_delays[destination_airport]['lat'], airport_delays[destination_airport]['lon'] \
            = dest_lat, dest_lon

        # Normalize delay percentage to match color scale (0.02 to 0.33)
        normalized_delay = 0.02 + (delay_percentage / 100) * (0.33 - 0.02)

        delay_color = map_delay_to_folium_color(normalized_delay)

        # Create a dotted line effect with alternating colors
        folium.PolyLine(
            locations=[(origin_lat, origin_lon), (dest_lat, dest_lon)],
            color=delay_color,
            weight=4.5,
            opacity=0.7,
            dash_array="5, 10"  # Dotted line effect
        ).add_to(flight_map)

        # Create the second polyline (with less opacity)
        folium.PolyLine(
            locations=[(origin_lat, origin_lon), (dest_lat, dest_lon)],
            color=delay_color,
            weight=4.5,
            opacity=0.5
        ).add_to(flight_map)

    # Add airport markers with the respective color based on average delay
    for airport, stats in airport_delays.items():
        if stats['count'] > 0:
            avg_delay = stats['total_delay'] / stats['count']
            normalized_avg_delay = 0.02 + (avg_delay / 100) * (0.33 - 0.02)
            delay_color = map_delay_to_folium_color(normalized_avg_delay)

            folium.Marker(
                location=[stats['lat'], stats['lon']],
                popup=f"Airport: {airport}, Avg Delay: {avg_delay:.2f}%",
                icon=folium.Icon(color=delay_color, icon="plane"),
            ).add_to(flight_map)

    add_color_scale(flight_map)

    flight_map.save("data/output/flight_map.html")
    print("flight map saved in data/output folder as flight_map.html")


def map_delay_to_folium_color(normalized_delay):
    """Map the normalized delay to one of 7 colors."""
    if normalized_delay < 0.11:
        return 'green'
    elif normalized_delay < 0.14:
        return 'lightgreen'
    elif normalized_delay < 0.17:
        return 'beige'
    elif normalized_delay < 0.21:
        return 'orange'
    elif normalized_delay < 0.26:
        return 'lightred'
    elif normalized_delay < 0.30:
        return 'red'
    else:
        return 'darkred'


def add_color_scale(flight_map):
    """Adds a gradient color bar (legend) to the map without a title."""
    colormap = branca.colormap.LinearColormap(
        colors=['green', 'yellow', 'red'],
        vmin=0.02, vmax=0.33
    )
    colormap.add_to(flight_map)
