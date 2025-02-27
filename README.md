# sqlalchemy-challenge

Database Schema
The SQLite database (hawaii.sqlite) contains two tables:

Measurement Table

id: Primary Key
station: Station ID
date: Observation date
prcp: Precipitation amount
tobs: Temperature observation
Station Table

id: Primary Key
station: Unique station ID
name: Station name
latitude: Latitude coordinate
longitude: Longitude coordinate
elevation: Elevation
Data Analysis Steps
1. Database Connection
The project uses SQLAlchemy ORM to connect to the hawaii.sqlite database:


from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

# Create engine and reflect tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to tables
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create session
session = Session(engine)
2. Precipitation Analysis
Retrieve the last 12 months of precipitation data from the Measurement table.
Convert results into a Pandas DataFrame.
Sort the data by date.
Visualize precipitation trends using Matplotlib.

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# Find the most recent date
most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

# Calculate the date one year ago
one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

# Query precipitation data for the last 12 months
precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

# Convert to Pandas DataFrame
precipitation_df = pd.DataFrame(precipitation_data, columns=['date', 'precipitation'])
precipitation_df = precipitation_df.dropna()  # Remove NaN values

# Plot precipitation data
plt.figure(figsize=(10,6))
plt.bar(precipitation_df['date'], precipitation_df['precipitation'], width=3, color='b', alpha=0.5)
plt.xticks(rotation=90)
plt.xlabel("Date")
plt.ylabel("Inches")
plt.title("Precipitation in the Last 12 Months")
plt.show()
3. Station Analysis
Find the total number of stations in the dataset.
Identify the most active station (station with the most observations).
Retrieve min, max, and avg temperatures for the most active station.
Visualize temperature data using a histogram.
Find the total number of stations

total_stations = session.query(Station).count()
print(f"Total number of stations: {total_stations}")  # Output: 9
Identify the most active station
python
Copy
from sqlalchemy import func

# Query the most active stations (station with most observations)
most_active_stations = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc())\
    .all()

most_active_station = most_active_stations[0][0]  # Extract the top station ID
print(f"Most active station: {most_active_station}")  # Output: 'USC00519281'
Retrieve min, max, and avg temperatures for the most active station
python
Copy
temperature_stats = session.query(func.min(Measurement.tobs),
                                  func.max(Measurement.tobs),
                                  func.avg(Measurement.tobs))\
    .filter(Measurement.station == most_active_station).all()

print(f"Temperature stats for {most_active_station}: Min={temperature_stats[0][0]}, Max={temperature_stats[0][1]}, Avg={temperature_stats[0][2]}")
Expected Output:

mathematica

Temperature stats for USC00519281: Min=54.0, Max=85.0, Avg=71.66
Plot Temperature Observations

# Query last 12 months of temperature observations for most active station
tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station)\
    .filter(Measurement.date >= one_year_ago).all()

# Convert to DataFrame
tobs_df = pd.DataFrame(tobs_data, columns=['tobs'])

# Plot histogram
tobs_df.plot.hist(bins=12, figsize=(10,6), legend=False)
plt.title(f"Temperature Observations for Station {most_active_station}")
plt.xlabel("Temperature (°F)")
plt.ylabel("Frequency")
plt.show()
Final Analysis & Observations
The dataset covers August 23, 2016 – August 23, 2017.
Average daily rainfall was 0.18 inches, with some days receiving up to 6.7 inches.
Honolulu generally experiences low rainfall, but occasional heavy downpours occur.
The most active station (USC00519281) recorded 2,772 observations.
Temperature trends show an average of 72°F, with a low of 54°F and a high of 85°F.
Most days are warm and pleasant, making Honolulu a great outdoor destination.
How to Run the Code
Install Dependencies
Ensure Python is installed and install required libraries:

pip install numpy pandas matplotlib sqlalchemy
Run the Jupyter Notebook
Open climate_analysis.ipynb and execute the cells to perform climate analysis.
Closing the Database Session
To ensure the database connection is properly managed, the session is closed at the end of the script:


# Close Session
session.close()
Next Steps
Develop a Flask API (app.py) to retrieve and serve climate data dynamically.
Expand analysis by comparing climate trends across multiple stations.
Build an interactive visualization dashboard for user-friendly insights.
Contact & Contributions
If you have any suggestions or improvements, feel free to contribute! 🚀

This README.md explains the project setup, code functionality, and key findings in a clear and structured way. Let me know if you'd like any modifications! 🚀






Developing app.py for this project involves creating a Flask API that serves climate data through various routes. Below is a step-by-step guide to help you build app.py for the Honolulu Climate Analysis API.

Step 1: Install Flask
Before proceeding, ensure Flask is installed in your environment:


pip install flask sqlalchemy pandas numpy
Step 2: Import Required Libraries
Create a new Python script called app.py, then import the necessary dependencies:


from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
Step 3: Set Up Database Connection
Connect Flask to the SQLite database (hawaii.sqlite) using SQLAlchemy:


# Create the Flask app
app = Flask(__name__)

# Create engine and reflect database tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Station = Base.classes.station
Measurement = Base.classes.measurement
Step 4: Define API Routes
Now, define the API endpoints:

1. Homepage Route (/)
This will list all available API routes:


@app.route("/")
def welcome():
    return (
        f"Welcome to the Honolulu Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Last 12 months of precipitation data<br/>"
        f"/api/v1.0/stations - List of weather stations<br/>"
        f"/api/v1.0/tobs - Temperature observations from the most active station<br/>"
        f"/api/v1.0/<start> - Temperature stats from a start date to the most recent date<br/>"
        f"/api/v1.0/<start>/<end> - Temperature stats for a given date range<br/>"
    )
2. Precipitation Route (/api/v1.0/precipitation)
Returns the last 12 months of precipitation data in JSON format.


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start a session
    session = Session(engine)
    
    # Find the most recent date
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
3. Stations Route (/api/v1.0/stations)
Returns a JSON list of all weather stations.


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query all station names
    results = session.query(Station.station).all()
    
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))

    return jsonify(station_list)
4. Temperature Observations Route (/api/v1.0/tobs)
Returns the last 12 months of temperature observations for the most active station.

python
Copy
@app.route("/api/v1.0/tobs")
def tobs():
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
5. Temperature Stats Route (Start Date: /api/v1.0/<start>)
Returns min, max, and avg temperature from a given start date to the most recent date.


@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
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
6. Temperature Stats Route (Start & End Date: /api/v1.0/<start>/<end>)
Returns min, max, and avg temperature for a given date range.


@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
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
Step 5: Run the Flask App
At the bottom of app.py, add:


if __name__ == "__main__":
    app.run(debug=True)
