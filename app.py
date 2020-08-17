import os
import numpy as np
from datetime import datetime as dt, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;startdate&gt;<br/>"
        f"/api/v1.0/&lt;startdate&gt;/&lt;enddate&gt;<br/><br/>"
        f"(Write 'startdate' and 'enddate' in %Y-%m-%d format, examples below)<br/>"
        f"/api/v1.0/2016-05-31<br/>"
        f"/api/v1.0/2016-05-31/2016-08-25"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Obtain last recorded date and the date one year before then
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.strptime(latest_date[0], "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d") # string to date, date - days, date to string
    
    # Query all precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year_date).all()

    session.close()

    # Create a dictionary from the row data and append to the list 'prcp_list'
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.id, Station.station, Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to the list 'station_list'
    station_list = []
    for station_id, station, name in results:
        station_dict = {}
        station_dict["ID"] = station_id
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Obtain last recorded date and the date one year before then
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.strptime(latest_date[0], "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d") # string to date, date - days, date to string
    
    # Query all stations and find most active station
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc())
    
    # Query tobs data from most active station
    active_desc = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == stations[0][0]).\
        filter(Measurement.date >= last_year_date).all()
    
    session.close()

    # Create a dictionary from the row data and append to the list 'tob_list'
    tob_list = []
    for date, tobs in active_desc:
        tob_dict = {}
        tob_dict["Date"] = date
        tob_dict["Temp"] = tobs
        tob_list.append(tob_dict)

    return jsonify(tob_list)


@app.route("/api/v1.0/<start>")
def start_only(start):
    session = Session(engine)

    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    results = session.query(Measurement.date,
                            func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    
    session.close()

    # Create a dictionary from the row data and append to the list 'all_dates'
    all_dates = []
    for date, tmin, tavg, tmax in results:
        dates_dict = {}
        dates_dict["Date"] = date
        dates_dict["TMIN"] = tmin
        dates_dict["TAVG"] = tavg
        dates_dict["TMAX"] = tmax
        all_dates.append(dates_dict)

    return jsonify(all_dates)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    results = session.query(Measurement.date,
                            func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    
    session.close()

    # Create a dictionary from the row data and append to the list 'all_dates'
    all_dates = []
    for date, tmin, tavg, tmax in results:
        dates_dict = {}
        dates_dict["Date"] = date
        dates_dict["TMIN"] = tmin
        dates_dict["TAVG"] = tavg
        dates_dict["TMAX"] = tmax
        all_dates.append(dates_dict)

    return jsonify(all_dates)
    

if __name__ == '__main__':
    app.run(debug=True)

