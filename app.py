# Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database
base = automap_base()
base.prepare(engine, reflect = True)

# Create save table references
measurement = base.classes.measurement
station = base.classes.station

# Create session
session = Session(engine)

# Setup Flask
app = Flask(__name__)

# Setup Flask Routes


@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    print("Received precipitation api request.")

    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(365)

     # Query for all the precipitation data
    precipitation_data = session.query(func.strftime("%Y-%m-%d", measurement.date), measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= begin_date).all()
    
    # Create Dictionaries
    results_dict = {}
    for result in precipitation_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    print("Received station api request.")

    # Query for the stations list
    stations = session.query(station).all()

    # Now create a list of dictionaries
    stations_list = []
    for station in stations:
        stations_dict = {}
        stations_dict["id"] = station.id
        stations_dict["station"] = station.station
        stations_dict["name"] = station.name
        stations_dict["latitude"] = station.latitude
        stations_dict["longitude"] = station.longitude
        stations_dict["elevation"] = station.elevation
        stations_list.append(stations_dict)

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    print("Received tobs api request.")

    # Define temp data for last year and find the max date, using that to calculate the beginning date
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date_string = final_date_query[0][0]
    final_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = final_date - dt.timedelta(365)

    # Find the temperature measurements for last year
    results = session.query(measurement).\
        filter(func.strftime("%Y-%m-%d", measurement.date) >= begin_date).all()

    # Create a list of dictionaries, one for each app route
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    print("Received only start date API request.")

    # Last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", measurement.date))).all()
    max_date = final_date_query[0][0]

    # Calculate the temperatures
    temps = calc_temps(start, max_date)

    # Now create a list of dictionaries
    start_list = []
    dates_dict = {'start_date': start, 'end_date': max_date}
    start_list.append(dates_dict)
    start_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    start_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    start_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list for a given start or start-end range."""
    print("Received start date and end date API request.")

    # Calculate the temperatures
    temps = calc_temps(start, end)

    # Now create a list of dictionaries
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug = False)