import os
import sys

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import data

# Initialize Flask app and data manager
app = Flask(__name__)
SQLITE_URI = f"""sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                         'data', 'db', 'flights.sqlite3'))}"""
data_manager = data.FlightData(SQLITE_URI)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger UI configuration
SWAGGER_URL = "/api/docs"
API_URL_PATH = "/static/swagger.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL_PATH,
    config={
        'app_name': 'Flight Data API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/static/swagger.json')
def serve_swagger():
    """
    Serves the Swagger JSON file from the static directory.
    """
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'swagger.json')


@app.route('/api/flight/<int:flight_id>', methods=['GET'])
def get_flight_by_id(flight_id):
    """
    Handles GET requests for the '/api/flight/<flight_id>' endpoint.
    - Retrieves flight details based on the provided flight ID.
    - Returns flight details if found, otherwise an empty response.
    :param flight_id: ID of the flight to retrieve
    :return: JSON response containing flight details or an empty list
    """
    results = data_manager.get_flight_by_id(flight_id)
    return jsonify([dict(row._mapping) for row in results])


@app.route('/api/flight/date', methods=['GET'])
def get_flights_by_date():
    """
    Handles GET requests for the '/api/flight/date' endpoint.
    - Retrieves a list of flights scheduled for the specified date.
    - Limits the results to a sample of 10 flights.
    :queryparam day: The day of the flight (integer, required)
    :queryparam month: The month of the flight (integer, required)
    :queryparam year: The year of the flight (integer, required)
    :return: JSON response containing a list of flights or an error message
    """
    day = request.args.get('day', type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    if not all([day, month, year]):
        return jsonify({'error': 'Missing date parameters'}), 400
    results = data_manager.get_flights_by_date(day, month, year)
    results = results[:10]
    return jsonify([dict(row._mapping) for row in results])


@app.route('/api/flight/routes', methods=['GET'])
def get_flight_routes_with_most_frequent_destinations():
    """
    Handles GET requests for the '/api/flight/routes' endpoint.
    - Retrieves a list of the most frequent flight routes.
    - Limits the response to 10 most frequent routes.
    :return: JSON response containing flight routes
    """
    results = data_manager.get_flight_routes_with_most_frequent_destinations()
    results = results[:10]
    return jsonify([dict(row._mapping) for row in results])


@app.route('/api/flight/delay/', methods=['GET'])
def get_delayed_flights():
    """
    Handles GET requests for the '/api/flight/delay/' endpoint.
    - Retrieves delayed flights filtered by airline or airport.
    - If an airline is provided, returns delayed flights for that airline.
    - If an airport is provided, returns delayed flights for that airport.
    - Limits the response to 10 results.
    :queryparam airline: Full name of the airline (string, optional)
    :queryparam airport: IATA code of the airport (string, optional)
    :return: JSON response containing delayed flights or an error message
    """
    airline = request.args.get('airline')
    airport = request.args.get('airport')

    if airline:
        results = data_manager.get_delayed_flights_by_airline(airline)
    elif airport:
        results = data_manager.get_delayed_flights_by_airport(airport)
    else:
        return jsonify({'error': 'Missing required parameter: airline or airport'}), 400

    results = results[:10]
    return jsonify([dict(row._mapping) for row in results])


@app.route('/api/flight/delay/percentage/', methods=['GET'])
def get_delay_percentage():
    """
    Handles GET requests for the '/api/flight/delay/percentage/' endpoint.
    - Retrieves the percentage of flight delays categorized by airline, hour, or airports.
    - Limits the response to 10 results when the category is 'airports'.
    :queryparam category: Category for delay percentage calculation (string, required)
                          Options: 'airline', 'hour', 'airports'
    :return: JSON response containing delay percentages or an error message
    """
    category = request.args.get('category')

    if category == 'airline':
        results = data_manager.get_delay_percentage_by_airline()
    elif category == 'hour':
        results = data_manager.get_delay_percentage_by_hour()
    elif category == 'airports':
        results = data_manager.get_delay_percentage_by_airports()
        results = results[:10]
    else:
        return jsonify({'error': 'Invalid or missing category parameter. '
                                 'Choose from airline, hour, or airports.'}), 400

    return jsonify([dict(row._mapping) for row in results])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
