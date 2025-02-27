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
