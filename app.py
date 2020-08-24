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

latestDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestDate = list(np.ravel(latestDate))[0]

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')
latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
latestDay = int(dt.datetime.strftime(latestDate, '%d'))

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')

# Setup Flask (@app) Routes


@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Surf's Up, it's vacation time!: Hawai'i Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/StartDate<br/>"
        f"/api/v1.0/StartDateEndDate<end>"
    )


@app.route("/api/v1.0/precipitaton")
def precipitation():
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/temperature")
def temperature():
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

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