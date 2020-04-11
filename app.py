## This is to continue my research on which Hawaiian 
# destination I'll be visiting.
## I'll be creating a Flask app for easy searches 
# of the database that will return in JSON format.
## These will include a landing page, a page for 
# precipitation data, stations, and best of all
# a place to query the minimum, maximum, and average temperature data
# with a given start or end date.


import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home page.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation page.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Queiries the last 12 months of precipitation data (2016-08-23 to 2017-08-23) into a list format (variable = latestyr_date_prcp). Casts this list into a dictionary (variable = year_prcp).
    Returns the JSON representation."""
    sel = [measurement.date,
      measurement.prcp]
    latestyr_date_prcp = session.query(*sel).\
    filter(measurement.date > '2016-08-23').\
    group_by(measurement.date).\
    order_by(measurement.date).all()
    year_prcp = {date:prcp for date, prcp in latestyr_date_prcp}
    return jsonify(year_prcp)

# Station page.
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station_list = session.query(measurement.station, station.name).filter(measurement.station == station.station).all()
    stn_dict = {station:name for station, name in station_list}
    return jsonify(stn_dict)

# Temperature Observed By Station page (TOBS)
@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data.
    Returns: a JSON file of date:tobs for the latest year of tobs data (2016-08-23 to 2017-08-23) for the most active station id(USC00519281)"""
    sel = [measurement.date, measurement.tobs]
    latest_year_tobs = session.query(*sel).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date > '2016-08-23').\
    group_by(measurement.date, measurement.station).all()
    year_tobs = {date:prcp for date, prcp in latest_year_tobs}
    return jsonify(year_tobs)

# Starting and ending date temperature search page.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start=None, end=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    if end is None:
        end = session.query(func.max(measurement.date))
        
    answer = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    answer = list(np.ravel(answer))
   
    return jsonify(answer)


session.close()

if __name__ == '__main__':
    app.run(debug=True)