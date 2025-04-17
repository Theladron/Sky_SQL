import logging

from sqlalchemy import create_engine, text

QUERY_FLIGHT_BY_ID = ("SELECT flights.*, "
                      "airlines.airline, "
                      "flights.ID as FLIGHT_ID, "
                      "flights.DEPARTURE_DELAY as DELAY "
                      "FROM flights JOIN airlines ON flights.airline = airlines.id "
                      "WHERE flights.ID = :id")

QUERY_FLIGHTS_BY_DATE = ("SELECT flights.*, "
                         "airlines.airline, "
                         "flights.ID as FLIGHT_ID, "
                         "flights.DEPARTURE_DELAY as DELAY "
                         "FROM flights JOIN airlines ON flights.airline = airlines.id "
                         "WHERE flights.DAY = :day "
                         "AND flights.MONTH = :month "
                         "AND flights.YEAR = :year")

QUERY_DELAYED_FLIGHTS_BY_AIRLINE = ("SELECT flights.*, "
                                    "airlines.airline, "
                                    "flights.ID as FLIGHT_ID, "
                                    "flights.DEPARTURE_DELAY as DELAY FROM flights "
                                    "JOIN airlines ON flights.airline = airlines.id "
                                    "WHERE airlines.AIRLINE = :airline "
                                    "AND flights.DEPARTURE_DELAY >= 20")

QUERY_DELAYED_FLIGHTS_BY_AIRPORT = ("SELECT flights.*, "
                                    "airlines.airline, "
                                    "flights.ID as FLIGHT_ID, "
                                    "flights.DEPARTURE_DELAY as DELAY FROM flights "
                                    "JOIN airlines ON flights.airline = airlines.id "
                                    "WHERE flights.ORIGIN_AIRPORT = :airport "
                                    "AND flights.DEPARTURE_DELAY >= 20")

QUERY_DELAY_PERCENTAGE_BY_AIRLINE = ("SELECT airlines.airline AS AIRLINE_NAME, "
                                     "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY >= 20 THEN 1 "
                                     "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS DELAY_PERCENTAGE "
                                     "FROM flights JOIN airlines ON flights.airline = airlines.id "
                                     "GROUP BY AIRLINE_NAME "
                                     "ORDER BY DELAY_PERCENTAGE DESC;")

QUERY_DELAY_PERCENTAGE_BY_HOUR = ("SELECT CAST(SUBSTR(flights.DEPARTURE_TIME, 1, 2) AS INTEGER) "
                                  "AS HOUR, "
                                  "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY >= 20 THEN 1 "
                                  "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS DELAY_PERCENTAGE "
                                  "FROM flights "
                                  "GROUP BY HOUR "
                                  "ORDER BY HOUR;")

QUERY_DELAY_PERCENTAGE_BY_AIRPORTS = ("SELECT flights.ORIGIN_AIRPORT, "
                                      "flights.DESTINATION_AIRPORT, "
                                      "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY >= 20 "
                                      "THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 "
                                      "AS DELAY_PERCENTAGE "
                                      "FROM flights "
                                      "GROUP BY flights.ORIGIN_AIRPORT, "
                                      "flights.DESTINATION_AIRPORT "
                                      "ORDER BY DELAY_PERCENTAGE DESC;")

QUERY_FLIGHT_ROUTES_WITH_DELAY_AND_AIRPORTS = ("WITH MostFrequentDestinations AS "
                                               "(SELECT ORIGIN_AIRPORT, DESTINATION_AIRPORT, "
                                               "COUNT(*) AS frequency "
                                               "FROM flights "
                                               "GROUP BY ORIGIN_AIRPORT, DESTINATION_AIRPORT "
                                               "ORDER BY frequency DESC) "
                                               "SELECT f.ORIGIN_AIRPORT, "
                                               "f.DESTINATION_AIRPORT, "
                                               "o.CITY AS ORIGIN_CITY, "
                                               "d.CITY AS DESTINATION_CITY, "
                                               "o.LATITUDE AS ORIGIN_LAT, "
                                               "o.LONGITUDE AS ORIGIN_LON, "
                                               "d.LATITUDE AS DESTINATION_LAT, "
                                               "d.LONGITUDE AS DESTINATION_LON, "
                                               "CAST(SUM(CASE WHEN f.DEPARTURE_DELAY >= 20 THEN 1 "
                                               "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 "
                                               "AS DELAY_PERCENTAGE "
                                               "FROM flights as f "
                                               "JOIN airports as o "
                                               "ON f.ORIGIN_AIRPORT = o.IATA_CODE "
                                               "JOIN airports as d "
                                               "ON f.DESTINATION_AIRPORT = d.IATA_CODE "
                                               "JOIN MostFrequentDestinations as mfd "
                                               "ON f.ORIGIN_AIRPORT = mfd.ORIGIN_AIRPORT "
                                               "AND f.DESTINATION_AIRPORT = mfd.DESTINATION_AIRPORT"
                                               " GROUP BY f.ORIGIN_AIRPORT, f.DESTINATION_AIRPORT, "
                                               "o.CITY, d.CITY, o.LATITUDE, o.LONGITUDE, "
                                               "d.LATITUDE, d.LONGITUDE "
                                               "ORDER BY delay_percentage DESC;")


class FlightData:
    """
    The FlightData class is a Data Access Layer (DAL) object that provides an
    interface to the flight data in the SQLITE database. When the object is created,
    the class forms connection to the sqlite database file, which remains active
    until the object is destroyed
    """

    def __init__(self, db_uri):
        """
        Initialize a new engine using the given database URI
        """
        self._engine = create_engine(db_uri)

    def _execute_query(self, query, params={}):
        """
        Execute an SQL query with the params provided in a dictionary, handles errors
        and returns a list of records (dictionary-like objects).
        :return: list of row objects if successful, else an empty list
        """
        try:
            with self._engine.connect() as connection:
                results = connection.execute(text(query), params)
                return results.mappings().all()
        except Exception as error:
            logging.error("Error executing query: %s", error)
            return []

    def get_flight_by_id(self, flight_id):
        """
        Searches for flight details using flight ID.
        :return: List of tuples containing flight details
        """
        params = {'id': flight_id}
        return self._execute_query(QUERY_FLIGHT_BY_ID, params)

    def get_flights_by_date(self, day, month, year):
        """
        Searches for flight details using the date with day/month/year, handles errors

        :return: List of tuples containing flight details
        """
        if not (1 <= day <= 31 and 1 <= month <= 12 and year > 1900):
            logging.warning("Invalid date parameters")
            return []
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(QUERY_FLIGHTS_BY_DATE, params)

    def get_delayed_flights_by_airline(self, airline):
        """
        Searches for delayed flights details using airline name, handles errors
        :return: List of tuples containing flight details
        """
        params = {'airline': airline}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

    def get_delayed_flights_by_airport(self, airport):
        """
        Searches for delayed flights details using airport IATA codes, handles errors
        :return: List of tuples containing flight details
        """
        params = {'airport': airport}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

    def get_delay_percentage_by_airline(self):
        """
        Fetches the percentage of delayed flights for each airline, handles errors
        :return: List of tuples containing flight route information
        """
        return self._execute_query(QUERY_DELAY_PERCENTAGE_BY_AIRLINE)

    def get_delay_percentage_by_hour(self):
        """
        Fetches the percentage of delayed flights for each hour, handles errors
        :return: List of tuples containing (hour, delay_percentage)
        """
        return self._execute_query(QUERY_DELAY_PERCENTAGE_BY_HOUR)

    def get_delay_percentage_by_airports(self):
        """
        Fetches the percentage of delayed flights for each combination of origin and
        destination airports, handles errors
        :return: List of tuples containing (origin_airport, destination_airport, delay_percentage)
        """
        return self._execute_query(QUERY_DELAY_PERCENTAGE_BY_AIRPORTS)

    def get_flight_routes_with_most_frequent_destinations(self):
        """
        Fetches the flight routes along with delay percentages
        and airport information (latitude, longitude), handles errors
        :return: List of tuples containing flight route information
        """
        return self._execute_query(QUERY_FLIGHT_ROUTES_WITH_DELAY_AND_AIRPORTS)

    def __del__(self):
        """
        Closes the connection to the database when the object is about to be destroyed
        """
        self._engine.dispose()
