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

# Setup Flask Routes

@app.route("/")
def main():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""

    print("Received precipitation api request.")

    # Query for the first and final dates
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")
    begin_date = max_date - dt.timedelta(365)

    # Query for all the precipitation data for all the dates
    precipitation_data = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()
    

    results_dict = {}
    for result in precipitation_data:
        results_dict[result[0]] = result[1]

    return jsonify(results_dict)