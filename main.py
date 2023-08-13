from flask import Flask, jsonify, request, abort
from flask_restful import Resource, Api

from marshmallow import Schema, fields

import json

# General thoughts:
# Depending on the size of the locales.js file size, it may be worth loading it only once and keep it in memory during runtime.
# For the forecast.js file it is likely worth scheduling a reload with, for instance, apscheduler in order to retrieve up-to-date forecast data at all times.
# For this example usecase we will load the locales.js and forecast.js from disk every time an API call makes it necessary. This may be slow if a lot of API calls are issued. We recommend to "cache" the data in memory at least for 20 minutes or so.

app = Flask(__name__)
api = Api(app)

# Argument parsing

class AutocompleteCityQuerySchema(Schema):
    user_input = fields.String(required=True)

class WeatherForecastQuerySchema(Schema):
    city_id = fields.Int(required=True)

autocompletecity_schema = AutocompleteCityQuerySchema()
weatherforecast_schema = WeatherForecastQuerySchema()

class AutocompleteCity(Resource):
    def get(self):
        # Validate parameters
        errors = autocompletecity_schema.validate(request.args)
        if errors:
            abort(400, str(errors))
        user_input_incomplete_city_name = request.args.get('user_input')
        output = {}
        with open('base/locales.json', 'r') as city_options_file:
            city_options_json = json.load(city_options_file)
            filtered = [{'id': city['id'], 'name': city['name'], 'state': city['state']} for city in city_options_json if user_input_incomplete_city_name in city['name']]
        output['results'] = filtered
        return jsonify(output)

class WeatherForecast(Resource):
    def get(self):
        # Validate parameters
        errors = weatherforecast_schema.validate(request.args)
        if errors:
            abort(400, str(errors))
        city_id = int(request.args.get('city_id'))
        filtered = None
        output = {}
        with open('base/weather.json', 'r') as forecast_file:
            forecast_json = json.load(forecast_file)
            filtered = [forecast for forecast in forecast_json if city_id == forecast['locale']['id']]
        if filtered:
            return jsonify(filtered)
        output['error'] = f'No weather forecast was found for your city. Please contact our support team and inform the requested city_id: {city_id}.'
        output['city_id'] = city_id
        return jsonify(output)
    
api.add_resource(AutocompleteCity, '/autocomplete_city')
api.add_resource(WeatherForecast, '/weatherforecast')

if __name__ == '__main__':
    app.run(debug=True)
