# Oh hey! Vacay!!- Technical Report

## Introduction
We have created a website that analyzes flight data to give you the ability to find a flight with the best fares with least delay. We have analyzed the data from the Bureau of Transportation Statistics (https://www.bts.gov/). For the scope of this project, we concentrated on data from January to December 2018. We took two datasets one focusing on the flight on time arrivals and the other flight fare data. We then removed the columns which were not required for the prediction analysis and loaded the clean data into the sqlite database and used the Decision Tree Regressor machine learning model to predict the arrival delay minutes and the best fare price. We used python flask app to create an app where user selects the desired route (Origin and Destination airports), airline and the month of travel and our model predicts the arrival delay minutes and the best fare for the route.

## On time Arrival Prediction:

Our website enables you to find the flight that’s most likely to arrive on time. To do this, you select the month of travel, your arrival and departure airport, the airline you wish to travel, and the “On Time” radio button and click “Predict”. Using historical data for your chosen route and month of travel, we use machine learning to predict the arrival delay for all airlines that fly that route ordered by delay in minutes. Your chosen airline is highlighted in the predictions to help you compare it with other airlines. In addition a piechart of arrival delays shows the breakdown of the delays by cause for the chosen airline. 

## Fare Prediction:

Furthermore, our website permits you to find the flight with the best fare. To do this, you choose your travel origin, destination, and the preferred airline, then select "Best Fares" option and click "Predict”.  We have used Decision Tree regressor machine learning model to predict the flight fare for your trip. The predicted fare for the chosen airline and the recommended airline based on the best fare for the trip would be shown. A table of all the available airlines and the predicted fares would be displayed, highlighting the chosen airline. The Latitude, Longitude values of the Origin and Destination was obtained using Google geocode API , which is used create a HighChart map with two paths connecting the origin and destination. The green path indicates my recommended airline with the best fare. The red path indicates your chosen airline. Click the paths to display the predicted values interactively in the visualization.


## Visualize 

<img src="https://github.com/arsasvk/project/blob/Sadhana/Images/arrival-delay-breakdown.png" alt="Arrival Delay" height="50%" width="50%">

<img src="https://github.com/arsasvk/project/blob/Sadhana/Images/best-flight-fare-compari.png" alt="Flight Map" height="50%" width="50%">


### Built With
* Pandas
* Python , Pandas
* Flask
* Scikit-learn (DecisionTreeRegressor)
* HTML5 , CSS, Bootstrap CSS
* Javascript
* HighCharts (Visualization)


### Author 
* Sadhana Kulkarni
* Meenakshi Nadimuthu
