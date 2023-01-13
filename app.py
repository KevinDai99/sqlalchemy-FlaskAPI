#######################################
# Import Dependencies 
#######################################

from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

latest_date = recent_date[0]

latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
one_year_ago = latest_date - dt.timedelta(days=365)

session.close()

# Flask Set-Up
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Perform a query to retrieve the data and precipitation scores
# ----------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Link session
    session = Session(engine)
    ttm = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    # Json conversion
    ttm_list = []
    for date, prcp in ttm:
        dict_ttm = {}
        dict_ttm["date"] = date
        dict_ttm["prcp"] = prcp
        ttm_list.append(dict_ttm)

    return jsonify(ttm_list)

# Stations 
# ----------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/stations")
def hawaii_stations():
    session = Session(engine)
    Stations_query = session.query(Station.name).all()
    session.close()
#json conversion 
    station_df = pd.DataFrame(Stations_query)
    return station_df.to_dict()


    
# Finding Most Active Station 
session = Session(engine)

most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

# Extract Most Active Station

most_active_station = most_active[0][0]
session.close()

# Query the dates and temperature observations of the most-active station for the previous year of data.
# ----------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    most_active_stat = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

# Json conversion
    ttm_most_active = []
    for date, tobs in most_active_stat:
        dict_active = {}
        dict_active["date"] = date
        dict_active["tobs"] = tobs
        ttm_most_active.append(dict_active)

    return jsonify(ttm_most_active)

# Min, Max, Avg Temperature for specific start date
# ----------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/<start>") 
def start_temp(start):
    session = Session(engine)
    averages = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
# Json conversion
    average_list = []

    for min_, max_, avg_ in averages:
        dict_temp = {}
        dict_temp["Min Temp"] = min_
        dict_temp["Max Temp"] = max_
        dict_temp["Avg Temp"] = avg_
        average_list.append(dict_temp)

    return jsonify(average_list)

# Min, Max, Avg Temperature for specific start & end date 
# ----------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/<start>/<end>") 
def start_end_temp(start, end):
    session = Session(engine)
    averages_start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
# Json conversion
    average_list_start_end = []
    for min_, max_, avg_ in averages_start_end:
        dict_temp_start_end = {}
        dict_temp_start_end["Min Temp"] = min_
        dict_temp_start_end["Max Temp"] = max_
        dict_temp_start_end["Avg Temp"] = avg_
        average_list_start_end.append(dict_temp_start_end)

    return jsonify(average_list_start_end)   


# Debug ON
if __name__ == '__main__':
    app.run(debug=True)



