import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end <br/>"
        f"Note: end statement is optional. Date format has to be %Y-%m-%d"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    """Return precipitation of certain date of each station"""
    # Query all date, station, precipitation
    results = session.query(Measurement.date, Measurement.station, Measurement.prcp).order_by(Measurement.date.desc()).all()

    #create a dictionary of the results with date as keys, station and prcp as values

    all_prcp = []
 
    for prcp in results:
        
        prcp_dict_nested={}
        prcp_dict_nested["station"] = prcp.station
        prcp_dict_nested["prcp"] = prcp.prcp

        prcp_dict = {}
        prcp_dict[prcp.date]=prcp_dict_nested

        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def station():
    """Return a list of stations"""
    results=session.query(Station.station).all()

    all_station=[]

    for station in results:
        all_station.append(station.station)
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point by station."""
    results=session.query(Measurement.station,Measurement.date,Measurement.tobs).filter(Measurement.date.between('2016-08-23','2017-08-23')).order_by(Measurement.date.desc()).all()

    """create a dictionary for the result"""
    all_tobs = []
 
    for tob in results:
        
        tobs_dict_nested={}
        tobs_dict_nested["station"] = tob.station
        tobs_dict_nested["tobs"] = tob.tobs

        tobs_dict = {}
        tobs_dict[tob.date]=tobs_dict_nested

        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")

def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start(string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    if start > '2017-08-23'or start<'2010-01-01':
        return jsonify({"error": f"Start date out of range. Must be smaller than 2017-08-23 and bigger than 2010-01-01"}), 404

    elif end is None:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

        #create a dictionary for the result"""
            
        result={}
        result['Minimum_temperature']=results[0][0]
        result['Average_temperature']=results[0][1]
        result['Maximum_temperature']=results[0][2]
 
        return jsonify(result)

    elif end is not None:
        if end > '2017-08-23' or end <'2010-01-01':
            return jsonify({"error": f"End date out of range. Must be smaller than 2017-08-23 and bigger than 2010-01-01"}), 404

        elif start>end:
            return jsonify({"error": f"Start date must be smaller than end date"}), 404
    
        else: 
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        #create a dictionary for the result"""
            
            result={}
            result['Minimum_temperature']=results[0][0]
            result['Average_temperature']=results[0][1]
            result['Maximum_temperature']=results[0][2]
 
            return jsonify(result)

    
if __name__ == '__main__':
    app.run(debug=True)
