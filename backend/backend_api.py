import logging
import os
import sys

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import data

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app and data manager
app = Flask(__name__)
SQLITE_URI = f"""sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                         'data', 'db', 'flights.sqlite3'))}"""
try:
    data_manager = data.FlightData(SQLITE_URI)
    logger.info("Database connection established.")
except Exception as e:
    logger.error("Error initializing database", exc_info=True)
    print(f"Error initializing data manager: {e}")
    data_manager = None

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


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Simple endpoint to check if the API is running.
    """
    if data_manager is None:
        return jsonify({'status': 'error', 'message': 'Database unavailable'}), 500
    return jsonify({'status': 'ok'}), 200


@app.route('/api/flight/<int:flight_id>', methods=['GET'])
def get_flight_by_id(flight_id):
    """
    Handles GET requests for the '/api/flight/<flight_id>' endpoint, handles errors.
    - Retrieves flight details based on the provided flight ID.
    - Returns flight details if found, otherwise an empty response.
    :param flight_id: ID of the flight to retrieve
    :return: JSON response containing flight details or an empty list
    """
    if data_manager is None:
        return jsonify({'error': 'Database not available'}), 500
    try:
        results = data_manager.get_flight_by_id(flight_id)
        if not results:
            return jsonify({'message': 'No flight found for the provided ID'}), 404
        return jsonify([dict(row) for row in results])
    except Exception as e:
        logger.error(f"error getting flight by ID: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/flight/date', methods=['GET'])
def get_flights_by_date():
    """
    Handles GET requests for the '/api/flight/date' endpoint, handles errors.
    - Retrieves a list of flights scheduled for the specified date.
    - Limits the results to a sample of 10 flights.
    :queryparam day: The day of the flight (integer, required)
    :queryparam month: The month of the flight (integer, required)
    :queryparam year: The year of the flight (integer, required)
    :return: JSON response containing a list of flights or an error message
    """
    if data_manager is None:
        return jsonify({'error': 'Database not available'}), 500
    try:
        day = request.args.get('day', type=int)
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        offset = request.args.get('offset', default=0, type=int)

        if not all([day, month, year]):
            return jsonify({'error': 'Missing date parameters'}), 400

        results = data_manager.get_flights_by_date(day, month, year)
        paged_results = results[offset:offset + 10]

        return jsonify([dict(row) for row in paged_results])
    except Exception as e:
        logger.error(f"error getting flights by date: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/flight/routes', methods=['GET'])
def get_flight_routes_with_most_frequent_destinations():
    """
    Handles GET requests for the '/api/flight/routes' endpoint, handles errors.
    - Retrieves a list of the most frequent flight routes.
    - Limits the response to 10 most frequent routes.
    :return: JSON response containing flight routes
    """
    if data_manager is None:
        return jsonify({'error': 'Database not available'}), 500
    try:
        offset = request.args.get('offset', default=0, type=int)
        results = data_manager.get_flight_routes_with_most_frequent_destinations()
        paged_results = results[offset:offset + 10]
        return jsonify([dict(row) for row in paged_results])
    except Exception as e:
        logger.error(f"error getting flight routes: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/flight/delay/', methods=['GET'])
def get_delayed_flights():
    """
    Handles GET requests for the '/api/flight/delay/' endpoint, handles errors.
    - Retrieves delayed flights filtered by airline or airport.
    - If an airline is provided, returns delayed flights for that airline.
    - If an airport is provided, returns delayed flights for that airport.
    - Limits the response to 10 results.
    :queryparam airline: Full name of the airline (string, optional)
    :queryparam airport: IATA code of the airport (string, optional)
    :return: JSON response containing delayed flights or an error message
    """
    if data_manager is None:
        return jsonify({'error': 'Database not available'}), 500
    try:
        airline = request.args.get('airline')
        airport = request.args.get('airport')
        offset = request.args.get('offset', default=0, type=int)

        if airline and airport:
            return jsonify(
                {'error': 'Please provide either an airline or an airport, not both'}), 400
        if airline:
            results = data_manager.get_delayed_flights_by_airline(airline)
        elif airport:
            results = data_manager.get_delayed_flights_by_airport(airport)
        else:
            return jsonify({'error': 'Parameter airline or airport is required'}), 400

        if not results:
            return jsonify({'message': 'No delayed flights found'}), 404

        paged_results = results[offset:offset + 10]
        return jsonify([dict(row) for row in paged_results])
    except Exception as e:
        logger.error(f"Error getting delayed flights: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/flight/delay/percentage/', methods=['GET'])
def get_delay_percentage():
    """
    Handles GET requests for the '/api/flight/delay/percentage/' endpoint, handles errors.
    - Retrieves the percentage of flight delays categorized by airline, hour, or airports.
    - Limits the response to 10 results when the category is 'airports'.
    :queryparam category: Category for delay percentage calculation (string, required)
                          Options: 'airline', 'hour', 'airports'
    :return: JSON response containing delay percentages or an error message
    """
    if data_manager is None:
        return jsonify({'error': 'Database not available'}), 500
    try:
        category = request.args.get('category')
        valid_categories = ['airline', 'hour', 'airports']

        if category not in valid_categories:
            return jsonify(
                {
                    'error': f'Invalid category. Valid categories: {", ".join(valid_categories)}'}), 400

        if category == 'airline':
            results = data_manager.get_delay_percentage_by_airline()
        elif category == 'hour':
            results = data_manager.get_delay_percentage_by_hour()
        elif category == 'airports':
            results = data_manager.get_delay_percentage_by_airports()

        if not results:
            return jsonify({'message': 'No delay percentages found'}), 404
        return jsonify([dict(row) for row in results])
    except Exception as e:
        logger.error(f"Error getting delay percentages: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
