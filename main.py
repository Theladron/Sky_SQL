from backend import data
from datetime import datetime
import sqlalchemy
from scripts import flight_map, heatmap, histogram

SQLITE_URI = 'sqlite:///data/db/flights.sqlite3'
IATA_LENGTH = 3


def visualize_flight_map(data_manager):
    """
    Fetches flight routes with delay percentages and calls the flight map plotting function
    with the amount of routes to show the user has entered.
    """
    # Fetch the flight routes (returns a list of tuples)
    flight_routes = data_manager.get_flight_routes_with_most_frequent_destinations()
    print("The map will show the flight paths with the most flights.")
    while True:
        number_of_routes = input("Please enter how many routes you want to see"
                                  " (or leave empty for all routes): ")
        if not number_of_routes:
            number_of_routes = len(flight_routes)
            break
        elif number_of_routes.isdigit():
            number_of_routes = int(number_of_routes)
            break
        else:
            print("Error. Input most be a positive, whole number or blank.")
    flight_map.plot_flight_map(flight_routes, number_of_routes)


def visualize_delay_by_airports(data_manager):
    """
    Fetches delay percentage by origin and destination airports and calls
    the heatmap plotting function.
    """
    results = data_manager.get_delay_percentage_by_airports()
    heatmap.plot_delay_heatmap_by_airports(results)


def visualize_delay_by_airline(data_manager):
    """
    Fetches delay percentage data and calls the histogram plotting function.
    """
    results = data_manager.get_delay_percentage_by_airline()
    histogram.plot_delayed_flights(results)


def visualize_delay_by_hour(data_manager):
    """
    Fetches delay percentage by hour and calls the histogram plotting function.
    """
    results = data_manager.get_delay_percentage_by_hour()
    histogram.plot_delay_by_hour(results)


def delayed_flights_by_airline(data_manager):
    """
    Asks the user for a textual airline name (any string will work here).
    Then runs the query using the data object method "get_delayed_flights_by_airline".
    When results are back, calls "print_results" to show them to on the screen.
    """
    airline_input = input("Enter airline name: ")
    results = data_manager.get_delayed_flights_by_airline(airline_input)
    print_results(results)


def delayed_flights_by_airport(data_manager):
    """
    Asks the user for a textual IATA 3-letter airport code (loops until input is valid).
    Then runs the query using the data object method "get_delayed_flights_by_airport".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        # Valide input
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = data_manager.get_delayed_flights_by_airport(airport_input)
    print_results(results)


def flight_by_id(data_manager):
    """
    Asks the user for a numeric flight ID,
    Then runs the query using the data object method "get_flight_by_id".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except Exception as e:
            print("Try again...")
        else:
            valid = True
    results = data_manager.get_flight_by_id(id_input)
    print_results(results)


def flights_by_date(data_manager):
    """
    Asks the user for date input (and loops until it's valid),
    Then runs the query using the data object method "get_flights_by_date".
    When results are back, calls "print_results" to show them to on the screen.
    """
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, '%d/%m/%Y')
        except ValueError as e:
            print("Try again...", e)
        else:
            valid = True
    results = data_manager.get_flights_by_date(date.day, date.month, date.year)
    print_results(results)


def print_results(results):
    """
    Get a list of flight results (List of dictionary-like objects from SQLAachemy).
    Even if there is one result, it should be provided in a list.
    Each object *has* to contain the columns:
    FLIGHT_ID, ORIGIN_AIRPORT, DESTINATION_AIRPORT, AIRLINE, and DELAY.
    """
    print(f"Got {len(results)} results.")
    for result in results:
        # turn result into dictionary
        result = result._mapping

        # Check that all required columns are in place
        try:
            delay = int(result['DELAY']) if result['DELAY'] else 0
            origin = result['ORIGIN_AIRPORT']
            dest = result['DESTINATION_AIRPORT']
            airline = result['AIRLINE']
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print("Error showing results: ", e)
            return

        # Different prints for delayed and non-delayed flights
        if delay and delay > 0:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}, Delay: {delay} Minutes")
        else:
            print(f"{result['ID']}. {origin} -> {dest} by {airline}")


def show_menu_and_get_input():
    """
    Show the menu and get user input.
    If it's a valid option, return a pointer to the function to execute.
    Otherwise, keep asking the user for input.
    """
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    # Input loop
    while True:
        try:
            choice = int(input())
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError as e:
            pass
        print("Try again...")

"""
Function Dispatch Dictionary
"""
FUNCTIONS = { 1: (flight_by_id, "Show flight by ID"),
              2: (flights_by_date, "Show flights by date"),
              3: (delayed_flights_by_airline, "Delayed flights by airline"),
              4: (delayed_flights_by_airport, "Delayed flights by origin airport"),
              5: (visualize_delay_by_airline, "Visualize airline delay percentages"),
              6: (visualize_delay_by_hour, "Visualize delay percentages by hour"),
              7: (visualize_delay_by_airports, "Visualize delay percentages by origin "
                                               "and destination airports"),
              8: (visualize_flight_map, "Visualize flight routes and delay percentages on map"),
              9: (quit, "Exit")
             }


def main():
    """Creates FlightData object instance and starts the main menu loop, allowing the user
    to call the different functions"""
    # Create an instance of the Data Object using our SQLite URI
    data_manager = data.FlightData(SQLITE_URI)

    # The Main Menu loop
    while True:
        choice_func = show_menu_and_get_input()
        if choice_func == quit:
            choice_func()
        choice_func(data_manager)


if __name__ == "__main__":
    main()