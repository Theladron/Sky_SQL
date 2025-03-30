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
        params = {'day': day, 'month': month, 'year': year}
        return self._execute_query(QUERY_FLIGHTS_BY_DATE, params)

    def get_delayed_flights_by_airline(self, airline):
        params = {'airline': airline}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRLINE, params)

    def get_delayed_flights_by_airport(self, airport):
        params = {'airport': airport}
        return self._execute_query(QUERY_DELAYED_FLIGHTS_BY_AIRPORT, params)

    def __del__(self):
        """
        Closes the connection to the databse when the object is about to be destroyed
        """
        self._engine.dispose()
