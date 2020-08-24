# Import Dependencies
import pandas as pd
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
Base = automap_base()
Base.prepare(engine, reflect = True)
Base.classes.keys()

# Create save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

# Setup Flask
app = Flask(__name__)

def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# Setup Flask Routes

@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Aloha! Welcome to the Surfs Up API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/Simple_Search<start><br/>"
        f"/api/v1.0/Advanced_Search<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of a dictionary where the date is the key and the value is the precipitation value"""
    print("Received precipitation api request.")

    # Find precipitation data for the last year.  First we find the last date in the database and use that to find the first day in the database.
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(366)

    # Find dates and precipitation amounts
    precip_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()
    
    # Prepare the dictionary with the date as the key and the prcp value as the value
    results_dict = {}
    for result in precip_data:
        results_dict[result[0]] = result[1]
    return jsonify(results_dict)


@app.route("/api/v1.0/stations")
def stations():
    results2 = session.query(Station.station, Station.name).all()
    sec_dict = list(np.ravel(results2))
    return jsonify(sec_dict)

if __name__ == '__main__':
    app.run(debug=True)