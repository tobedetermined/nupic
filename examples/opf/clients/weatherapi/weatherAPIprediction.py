#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------


"""A simple client to create a CLA model for weather prediction from online weather data."""

import csv, datetime, os, time, json, urllib2
import model_params_weather

from nupic.frameworks.opf.modelfactory import ModelFactory

def createModel():
  return ModelFactory.create(model_params_weather.MODEL_PARAMS)

def startFile():
	sessionPath = os.path.expanduser("output.csv")
	headersForFile = ['timestamp,', 'temperature,', 'humidity,', 'pressure,', 'visibility,', 'windspeedMiles,', 'predicted windspeedMiles']
	g = open(sessionPath, 'w')
	for s in headersForFile:
		g.write (s)
	g.write ('\n')
	g.close()

def writeRecord(record, predictionvalue):
	sessionPath = os.path.expanduser("output.csv")
	g = open(sessionPath, 'a')
	for s in record:
		g.write (s + ',')
	g.write (str(predictionvalue) + '\n')
	g.close

def weatherAPICall():
	########################################################################
	# please create your own API key at http://worldweatheronline.com/
	########################################################################
	response = urllib2.urlopen('http://api.worldweatheronline.com/free/v1/weather.ashx?q=redwood+city&format=json&extra=localObsTime&num_of_days=1&key=kh9vcvadfmwrscpfcnh9nknh')
	return response

def weatherPrediction():
  model = createModel()
  model.enableInference({'predictionSteps': [1, 5],
                         'predictedField': 'windspeedMiles',
                         'numRecords': 4000})
  headers = ['timestamp', 'temperature', 'humidity', 'pressure', 'visibility', 'windspeedMiles'] 
  startFile()
  i = 1
  while True:
	response = weatherAPICall()
	data = json.load(response)
	current = data['data']['current_condition']
	record = [current[0]['localObsDateTime'], current[0]['temp_C'], current[0]['humidity'], current[0]['pressure'], current[0]['visibility'], current[0]['windspeedMiles']]
	modelInput = dict(zip(headers, record))
	modelInput["temperature"] = float(modelInput["temperature"])
	modelInput["humidity"] = float(modelInput["humidity"])
	modelInput["pressure"] = float(modelInput["pressure"])
	modelInput["visibility"] = float(modelInput["visibility"])
	modelInput["windspeedMiles"] = float(modelInput["windspeedMiles"])
	modelInput["timestamp"] = datetime.datetime.strptime(modelInput["timestamp"], "%Y-%m-%d %I:%M %p")
	result = model.run(modelInput)
	print result
	print current[0]['localObsDateTime']
	print result.inferences['multiStepBestPredictions']
	predictionvalue = result.inferences['prediction'][7]
	print predictionvalue
	writeRecord(record, predictionvalue)
	print i
	i += 1
	time.sleep(15)

if __name__ == "__main__":
  weatherPrediction()
