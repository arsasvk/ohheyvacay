#import dependencies

import os

import pandas as pd
import numpy as np
import collections


from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from pprint import pprint
import json
import csv, sqlite3
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect, desc, and_, or_
import datetime
from predictfare import predictMarketFare, predictallairfare , findlatlng
from fareapp import fareapp

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(fareapp)


# Dictionary of month to monthId
month_conv = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

###############################################################################
# Database Setup
###############################################################################
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Resources/data/ontime.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)
ontime = Base.classes.ontime_data

stmt = db.session.query(ontime).statement
ontime_data = pd.read_sql_query(stmt, db.session.bind) 

#################################################################################

# Group by airline and airlineId 
airline_groups = ontime_data.groupby(
    ['Airline', 'DOT_ID_Operating_Airline']
)['Airline'].unique().to_dict().keys()  

# Convert airline-airlineId groups to a dictionary of airline-airlineId pairs
airline_conv = {}
for item in list(airline_groups):
    airline_conv[item[0]] = item[1]

# Group by airport and airportId and convert to dictionary airport-airportId pairs
airport_conv = {}
airport_groups = ontime_data.groupby(['Origin', 'OriginAirportID'])['Origin'].unique().to_dict().keys()
for item in list(airport_groups):
    airport_conv[item[0]] = item[1]


# Setup ML and train the data 
y = ontime_data["ArrDelayMinutes"] 
ontime_features = ["Month","DOT_ID_Operating_Airline", "OriginAirportID", "DestAirportID"]
X = ontime_data[ontime_features]  # features to help predict the data

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

ontimemodel = DecisionTreeRegressor(random_state=1)

ontimemodel.fit(train_X,train_y) # training the model


# API to the home page 
@app.route("/", methods=["GET"])
def index():
    """Return the homepage."""
    return render_template("index.html")


@app.route("/slides", methods=["GET"])
def slides():
    """Return the homepage."""
    return render_template("slides.html")

@app.route("/aboutus", methods=["GET"])
def aboutus():
    """Return the homepage."""
    return render_template("aboutus.html")


# API to return json of month-monthId pairs
@app.route("/month", methods=["GET"])
def month():
    """"Return months for month drop down"""
    return jsonify(month_conv)

# API to return json of airport-airportId pairs
@app.route("/airports", methods=["GET"])
def airports():
    """"Return airports for airport drop down"""
    return jsonify(airport_conv)

# API to return json of airline-airlineId pairs
@app.route("/airline", methods=["GET"])
def airline():
    """"Return airline for airline drop down"""
    return jsonify(airline_conv)

# API reconvert the airline codes to airline names
@app.route("/getAirlineName/<airlineId>", methods=["GET"])
def getAirlineName(airlineId):
    """"Return airline for airline drop down"""
    airlineName = "unknown"
    for airline, airlineCode in airline_conv.items():
        if int(airlineId) == airlineCode:
            airlineName = airline
    return jsonify(airlineName)

def getRowCount(month, airline, origin, destination):
    airlineId = airline_conv[airline]
    return ontime_data.loc[(ontime_data['Month'] == int(month)) &
                            (ontime_data['DOT_ID_Operating_Airline'] == int(airlineId)) &
                            (ontime_data['OriginAirportID'] == int(origin)) &
                            (ontime_data['DestAirportID'] == int(destination))].shape[0]

# @app.route("/rowCount/<month>/<origin>/<destination>")
# def rowCount(month, origin, destination):
#     rowCounts = {}
#     for airline, airlineCode in airline_conv.items():
#         rowCounts[airline] = getRowCount(month, airline, origin, destination)
#     return jsonify(rowCounts)


# API to fetch jsonify values of prediction sorted by delay minutes
@app.route("/predict/<month>/<origin>/<destination>", methods=["GET"])
def predict(month, origin, destination):
    val_predictions = {}
    for airline, airlineCode in airline_conv.items():
        if getRowCount(month, airline, origin, destination) == 0:          
            continue
        invalue = [month, airlineCode, origin, destination]
    
        val_predictions[airline] = int(ontimemodel.predict([invalue])[0])

    return jsonify(val_predictions)

# API to fetch counts for each arrival delay type for the specified month, airline
# and route.
@app.route("/visualize/<month>/<airline>/<origin>/<destination>", methods=["GET"])
def visualize(month, airline, origin, destination):
    select_df = ontime_data.loc[(ontime_data['Month'] == int(month)) &
                                (ontime_data['DOT_ID_Operating_Airline'] == int(airline)) &
                                (ontime_data['OriginAirportID'] == int(origin)) &
                                (ontime_data['DestAirportID'] == int(destination))]

    chartData = {}
    if select_df.shape[0] == 0:
        return jsonify(chartData)   

    chartData['CarrierDelay'] = int(select_df.loc[select_df['CarrierDelay'] > 0].count()['Month'])
    chartData['WeatherDelay'] = int(select_df.loc[select_df['WeatherDelay'] > 0].count()['Month'])
    chartData['NASDelay'] = int(select_df.loc[select_df['NASDelay'] > 0].count()['Month'])
    chartData['SecurityDelay'] = int(select_df.loc[select_df['SecurityDelay'] > 0].count()['Month'])
    chartData['LateAircraftDelay'] = int(select_df.loc[select_df['LateAircraftDelay'] > 0].count()['Month'])
    chartData['OnTime'] = int(select_df.loc[select_df['ArrDelayMinutes'] == 0].count()['Month'])
    
    return jsonify(chartData)

   
if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
