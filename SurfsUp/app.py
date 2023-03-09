import datetime as dt

from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Create session from Python to the DB
session = Session(engine)

#################################################
# Set up Flask and landing page
#################################################
app = Flask(__name__)

# Starting Date (12 months ago)
start_date = '2016-08-23'

@app.route("/")
def welcome():
    return (
        f"<p>Welcome to the Home page of the Hawaii weather API!</p>"
        f"<p>Usages of this API:</p>"
        f"/api/v1.0/precipitation<br/>This route returns a JSON dictionary of the percipitation data for the dates between 8/23/16 and 8/23/17.<br/><br/>"
        f"/api/v1.0/stations<br/>This route returns a JSON list of the weather stations in the database.<br/><br/>"
        f"/api/v1.0/tobs<br/>This route returns a JSON list of the temperatures observed (tobs) for each station for the dates between 8/23/16 and 8/23/17.<br/><br/>"
        f"/api/v1.0/selected_start_date<br/>This route returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the selected start date and 8/23/17.<br/><br/>"
        f"/api/v1.0/start_date/end_date<br/>This route returns a JSON list of the minimum, average, and max temperature for the dates between 8/23/16 and 8/23/17.<br/><br/>"
    )

# /api/v1.0/precipitation
# First, queries the temperature observations for each date from the last year.
# Next, it converts the result to a Dictionary using date as the key and observed temperature as the value.
# Finally, it returns a JSON representation of the created dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query db for daily tobs from past year
    prcp_result = session.query(measurement.date, func.avg(measurement.prcp)).filter(measurement.date >= start_date).group_by(measurement.date).all()
    
    # Create key and value lists for dictionary creation
    prcp_keys = []
    prcp_values = []
    for item in range(len(prcp_result)):
        prcp_keys.append(prcp_result[item][0])
        prcp_values.append(prcp_result[item][1])
    
    # Create dictionary from key and value list items
    prcp_dictionary = dict(zip(prcp_keys, prcp_values))

    # Return JSON representation of dictionary
    return jsonify(prcp_dictionary)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Query db to get list of stations
    station_result = session.query(station.station, station.name).all()
    
    # Create list
    station_list = []
    for item in range(len(station_result)):
        station_list.append([station_result[item][0],station_result[item][1]])
    
    # Return JSON representation of list
    return jsonify(station_list)


# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year for the most active station (USC00519281)
@app.route("/api/v1.0/tobs")
def tobs():
    # Query DB for temperature data for previous year for most active station (USC00519281)
    tobs_results = session.query(measurement.date, measurement.station, measurement.tobs).filter(measurement.date >= start_date).filter(measurement.station == 'USC00519281').all()
    
    # Create list
    tobs_list = []
    for item in range(len(tobs_results)):
        tobs_list.append([tobs_results[item][0],tobs_results[item][1],tobs_results[item][2]])
    
    return jsonify(tobs_list)


# /api/v1.0/<selected_start_date>
# When given the start only, calculate MIN, AVG, and MAX temperatures for all dates greater than and equal to the start date and return the results as a JSON list.
@app.route("/api/v1.0/<selected_start_date>")
def data_from_start_date(selected_start_date):
    # Query DB for temperature measurements from selected start date to most recent date
    temperature_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= selected_start_date).all()

    # Create list
    temperature_list = []
    for item in range(len(temperature_results)):
        temperature_list.append([temperature_results[item][0],temperature_results[item][1],temperature_results[item][2]])
    
    # Return JSON representation of list
    return jsonify(temperature_list)


# /api/v1.0/<start>/<end>
# Return a JSON list of the minimum, average, and max temperature for a given date range (inclusive).
@app.route("/api/v1.0/<start>/<end>")
def data_from_date_range(start_date,end_date):
    # Query DB for temperature measurements in selected date range
    multi_date_temp_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    
    # Create list
    temperature_list = []
    for item in range(len(multi_date_temp_results)):
        temperature_list.append([multi_date_temp_results[item][0],multi_date_temp_results[item][1],multi_date_temp_results[item][2]])
    
    # Return JSON representation of list
    return jsonify(temperature_list)

if __name__ == "__main__":
    app.run(debug=True)