import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurements = Base.classes.measurement
stations = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurements.date, measurements.prcp).filter(measurements.date >= last_year).all()
    session.close()
    return jsonify(dict(results))


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(stations.station).group_by(stations.station).all()
    session.close()
    all_stations=list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(measurements.date, measurements.tobs).\
        filter(measurements.date > query_date).\
        filter(measurements.station == "USC00519281").\
        order_by(measurements.date).all()

    session.close()

    return jsonify(dict(results))

@app.route("/api/v1.0/<start_date>")
def start(start_date):
    session = Session(engine)

    try:
        startdate = dt.datetime.strptime(start_date, "%d-%m-%Y").date()
        sel = [func.min(measurements.tobs),
            func.max(measurements.tobs),
            func.avg(measurements.tobs)]
        
        results = session.query(*sel).\
            filter(measurements.date >= startdate).all()
    except:
        session.close()
        return "Invalid start date entered", 404

    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    session = Session(engine)

    try:
        startdate = dt.datetime.strptime(start_date, "%d-%m-%Y").date()
        enddate = dt.datetime.strptime(end_date, "%d-%m-%Y").date()
        sel = [func.min(measurements.tobs),
            func.max(measurements.tobs),
            func.avg(measurements.tobs)]
        
        results = session.query(*sel).\
            filter(measurements.date >= startdate).\
            filter(measurements.date <= enddate).all()
    except:
        session.close()
        return "Invalid start or end date entered", 404

    session.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)