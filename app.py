import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


# connect to database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# existing database
Base = automap_base()

Base.prepare(engine, reflect=True)

# create references
measurement = Base.classes.measurement
station = Base.classes.station


# set up flask

app = Flask(__name__)


# api routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session
    session = Session(engine)

    # query dates and precipitation 
    results =   session.query(measurement.date, measurement.prcp).\
                order_by(measurement.date).all()

    # Convert to list of dictionaries to jsonify
    prcp_and_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_and_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_and_date_list)

@app.route("/api/v1.0/stations")
def stations():
    # create session
    session = Session(engine)

    stations = {}

    # Query 
    results = session.query(station.station, station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # session
    session = Session(engine)

    # query for last date and date a year ago
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    previous_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query dates and temps
    results =   session.query(measurement.date, measurement.tobs).\
                filter(measurement.date >= last_year_date).\
                order_by(measurement.date).all()

    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results =   session.query(  measurement.date,\
                                func.min(measurement.tobs), \
                                func.avg(measurement.tobs), \
                                func.max(measurement.tobs)).\
                        filter(measurement.date >= start).\
                        group_by(measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results =   session.query(  measurement.date,\
                                func.min(measurement.tobs), \
                                func.avg(measurement.tobs), \
                                func.max(measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)