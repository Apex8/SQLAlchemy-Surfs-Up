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
        f"Welcome to the Surfs Up API! Aloha!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/Simple_Search<start><br/>"
        f"/api/v1.0/Advanced_Search<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>="2016-08-23").all()
    prec_dict = list(np.ravel(precipitation))
    return jsonify(prec_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station, Station.name).all()
    stat_dict = list(np.ravel(stations))
    return jsonify(stat_dict)


@app.route("/api/v1.0/temperature")
def temperature():
    temperature = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>="2016-08-23").filter(Measurement.date<="2017-08-23").all()
    temp_dict = list(np.ravel(temperature))
    return jsonify(temp_dict)


@app.route("/api/v1.0/Simple_Search<date>")
def Simple_Search(date):
    Simple_Search = session.query((Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
            filter(Measurement.date)>=date).all()
            
if __name__ == '__main__':
    app.run(debug=True)