# Import Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect Database
base = automap_base()
base.prepare(engine, reflect = True)

# Create save table references
Measurement = base.classes.measurement
Station = base.classes.station

# Create session
session = Session(engine)
inspector = inspect(engine)
inspector.get_table_names()

# Setup Flask
app = Flask(__name__)

# Setup Flask (@app) Routes


@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/Precipitation<br/>"
        f"/api/v1.0/Stations<br/>"
        f"/api/v1.0/Tobs<br/>"
        f"/api/v1.0/StartDate<br/>"
        f"/api/v1.0/StartDateEndDate<end>"
    )


@app.route("/api/v1.0/Precipitation")
def Precipitation():
    """Return the JSON representation of your dictionary."""
    print("Received precipitation api request.")

    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(365)

     # Query for all the precipitation data
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()
    
    # Create Dictionaries
    results_dict = {}
    for result in precipitation_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)


@app.route("/api/v1.0/Stations")
def Stations():
    """Return a JSON list of stations from the dataset."""
    print("Received station api request.")

    # Query for the stations list
    stations = session.query(Station.station, Station.name).all()

    # Now create a list of dictionaries
    stations_list = []
    for station in stations:
        stations_dict = {}
        stations_dict["id"] = Station.id
        stations_dict["station"] = Station.station
        stations_dict["name"] = Station.name
        stations_dict["latitude"] = Station.latitude
        stations_dict["longitude"] = Station.longitude
        stations_dict["elevation"] = Station.elevation
        stations_list.append(stations_dict)

    return jsonify(stations_list)


@app.route("/api/v1.0/Tobs")
def Tobs():
    """Return a JSON list of temperature observations for the previous year."""
    print("Received tobs api request.")

    # Define temp data for last year and find the max date, using that to calculate the beginning date
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    final_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = final_date - dt.timedelta(365)

    # Find the temperature measurements for last year
    temp_year = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    # Create a list of dictionaries, one for each app route
    tobs_list = []
    for result in temp_year:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/StartDate")
def StartDate(start):
    print("Received only start date API request.")

    # Last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    # Calculate the temperatures
    temps = Measurement(start, max_date)

    # Now create a list of dictionaries
    start_list = []
    dates_dict = {'start_date': start, 'end_date': max_date}
    start_list.append(dates_dict)
    start_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    start_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    start_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(start_list)

@app.route("/api/v1.0/StartDateEndDate")
def StartDateEndDate(start, end):
    """Return a JSON list for a given start or start-end range."""
    print("Received start date and end date API request.")

    # Calculate the temperatures
    temps = Measurement(start, end)

    # Now create a list of dictionaries
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)

if __name__ == "__main__":
    app.run(debug = True)