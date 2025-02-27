import os
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

#################################################
# Database Setup
#################################################

# Find the absolute path to the database file
db_path = os.path.join(os.path.dirname(__file__), "Resources/hawaii.sqlite")

# Create engine using the correct database path
engine = create_engine(f"sqlite:///{db_path}")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)  # Fix for SQLAlchemy 2.0

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

# Initialize Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# 1. Homepage Route - List all available routes
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Welcome to the Honolulu Climate API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations from the most active station<br/>"
        f"/api/v1.0/&lt;start&gt; - Temperature stats from a start date to the most recent date<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; - Temperature stats for a given date range<br/>"
    )

# 2. Precipitation Route - Returns last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as a JSON dictionary."""
    session = Session(engine)
    
    # Find the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert query results to dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_dict)

# 3. Stations Route - Returns a JSON list of all stations
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all weather stations."""
    session = Session(engine)

    # Query all station names
    results = session.query(Station.station).all()
    
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

# 4. Temperature Observations Route - Returns last 12 months of tobs data for the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations (tobs) for the most active station in the last 12 months."""
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Find the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Calculate one year ago from the most recent date
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query temperature observations for last 12 months for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert to a list
    tobs_list = list(np.ravel(results))

    return jsonify(tobs_list)

# 5. Temperature Stats Route (Start Date) - Returns min, max, and avg temperature from a start date
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return min, max, and avg temperature from the start date to the most recent date."""
    session = Session(engine)

    # Query min, max, and avg temperature from the given start date
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Convert query result into a dictionary
    temp_stats = {
        "Min Temperature": results[0][0],
        "Average Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }

    return jsonify(temp_stats)

# 6. Temperature Stats Route (Start & End Date) - Returns min, max, and avg temperature for a date range
@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return min, max, and avg temperature for a given date range."""
    session = Session(engine)

    # Query min, max, and avg temperature between start and end dates
    results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Convert query result into a dictionary
    temp_stats = {
        "Min Temperature": results[0][0],
        "Average Temperature": results[0][1],
        "Max Temperature": results[0][2]
    }

    return jsonify(temp_stats)

#################################################
# Run Flask App
#################################################

if __name__ == "__main__":
    app.run(debug=True)