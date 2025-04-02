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
                                    "WHERE airlines.AIRLINE = :airline")

QUERY_DELAYED_FLIGHTS_BY_AIRPORT = ("SELECT flights.*, "
                                    "airlines.airline, "
                                    "flights.ID as FLIGHT_ID, "
                                    "flights.DEPARTURE_DELAY as DELAY FROM flights "
                                    "JOIN airlines ON flights.airline = airlines.id "
                                    "WHERE flights.ORIGIN_AIRPORT = :airport")

QUERY_DELAY_PERCENTAGE_BY_AIRLINE = ("SELECT airlines.airline, "
                                     "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY > 0 THEN 1 "
                                     "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS delay_percentage "
                                     "FROM flights JOIN airlines ON flights.airline = airlines.id "
                                     "GROUP BY airlines.airline "
                                     "ORDER BY delay_percentage DESC;")

QUERY_DELAY_PERCENTAGE_BY_HOUR = ("SELECT CAST(SUBSTR(flights.DEPARTURE_TIME, 1, 2) AS INTEGER) "
                                  "AS hour, "
                                  "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY > 0 THEN 1 "
                                  "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 AS delay_percentage "
                                  "FROM flights "
                                  "GROUP BY hour "
                                  "ORDER BY hour;")

QUERY_DELAY_PERCENTAGE_BY_AIRPORTS = ("SELECT flights.ORIGIN_AIRPORT, "
                                      "flights.DESTINATION_AIRPORT, "
                                      "CAST(SUM(CASE WHEN flights.DEPARTURE_DELAY > 0 "
                                      "THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 "
                                      "AS delay_percentage "
                                      "FROM flights "
                                      "GROUP BY flights.ORIGIN_AIRPORT, "
                                      "flights.DESTINATION_AIRPORT "
                                      "ORDER BY delay_percentage DESC;")

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
                                               "CAST(SUM(CASE WHEN f.DEPARTURE_DELAY > 0 THEN 1 "
                                               "ELSE 0 END) AS FLOAT) / COUNT(*) * 100 "
                                               "AS delay_percentage "
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
    until the object is destroyed.
    """

    def __init__(self, db_uri):
        """
        Initialize a new engine using the given database URI
        """
        self._engine = create_engine(db_uri)

    def _execute_query(self, query, params):
        """
        Execute an SQL query with the params provided in a dictionary,
        and returns a list of records (dictionary-like objects).
        If an exception was raised, print the error, and return an empty list.
        """
        with self._engine.connect() as connection:
            results = connection.execute(text(query), params)
        return results.fetchall()

    def get_flight_by_id(self, flight_id):
        """
        Searches for flight details using flight ID.
        If the flight was found, returns a list with a single record.
        """
        params = {'id': flight_id}
        return self._execute_query(QUERY_FLIGHT_BY_ID, params)

    def get_flights_by_date(self, day, month, year):
        """
        Searches for flight details using the date with day/month/year.
        If the flight was found, returns a list with all the records.
        """
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(QUERY_FLIGHTS_BY_DATE, params)

    def get_delayed_flights_by_airline(self, airline):
        """
        Searches for delayed flights details using airline name.
        If the flight was found, returns a list with all the records.
        """
        params = {'airline': airline}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

    def get_delayed_flights_by_airport(self, airport):
        """
        Searches for delayed flights details using airport IATA codes.
        If the flight was found, returns a list with all the records.
        """
        params = {'airport': airport}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

    def get_delay_percentage_by_airline(self):
        """
        Fetches the percentage of delayed flights for each airline.

        :return: List of tuples containing (airline_name, delay_percentage)
        """
        with self._engine.connect() as connection:
            results = connection.execute(text(QUERY_DELAY_PERCENTAGE_BY_AIRLINE))
            return results.fetchall()

    def get_delay_percentage_by_hour(self):
        """
        Fetches the percentage of delayed flights for each hour.
        :return: List of tuples containing (hour, delay_percentage)
        """
        with self._engine.connect() as connection:
            results = connection.execute(text(QUERY_DELAY_PERCENTAGE_BY_HOUR))
            return results.fetchall()

    def get_delay_percentage_by_airports(self):
        """
        Fetches the percentage of delayed flights for each combination of origin and
        destination airports.
        :return: List of tuples containing (origin_airport, destination_airport, delay_percentage)
        """
        with self._engine.connect() as connection:
            results = connection.execute(text(QUERY_DELAY_PERCENTAGE_BY_AIRPORTS))
            return results.fetchall()

    def get_flight_routes_with_most_frequent_destinations(self):
        """
        Fetches the flight routes along with delay percentages,
        and airport information (latitude, longitude).
        :return: List of tuples containing flight route information
        """
        with self._engine.connect() as connection:
            results = connection.execute(text(QUERY_FLIGHT_ROUTES_WITH_DELAY_AND_AIRPORTS))
            return results.fetchall()

    def __del__(self):
        """
        Closes the connection to the databse when the object is about to be destroyed
        """
        self._engine.dispose()
