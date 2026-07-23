import requests
import schedule
import time
import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# -----------------------------------
# SETUP
# -----------------------------------

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

DATA_FILE = "data/commute_data.csv"

os.makedirs("data", exist_ok=True)

# -----------------------------------
# CONFIG
# -----------------------------------

CITIES = {
	"San Jose, CA": {
		"latitude": 37.310651,
		"longitude": -121.930414
	},
	"San Francisco, CA": {
		"latitude": 37.772165,
		"longitude": -122.430406
	},
	"Redwood City, CA": {
		"latitude": 37.485886,
		"longitude": -122.228169
	},
	"San Mateo, CA": {
		"latitude": 37.563072,
		"longitude": -122.324029
	}
}

WORK_LOCATIONS = {
	"San Francisco, CA": {
		"latitude": 37.772165,
		"longitude": -122.430406
	},
	"Milpitas, CA": {
		"latitude": 37.428676,
		"longitude": -121.899718
	}
}

# -----------------------------------
# GOOGLE MAPS API
# -----------------------------------

def get_travel_time(origin, destination, travelMode):
	url = "https://routes.googleapis.com/directions/v2:computeRoutes?key=" + API_KEY

	params = {
		"origin":{
			"location":{
				"latLng":{
					"latitude": origin["latitude"],
					"longitude": origin["longitude"]
				}
			}
		},
		"destination":{
			"location":{
				"latLng":{
					"latitude": destination["latitude"],
					"longitude": destination["longitude"]
				}
			}
		},
		"travelMode": travelMode,
		"routingPreference": "TRAFFIC_AWARE" if travelMode == "DRIVE" else None,
		"computeAlternativeRoutes": False,
		"routeModifiers": {
			"avoidTolls": False,
			"avoidHighways": False,
			"avoidFerries": False
		},
		"languageCode": "en-US",
		"units": "IMPERIAL"
	}

	headers = {
 		"Content-Type": "application/json",
 		"X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline",
	}

	response = requests.post(url, json=params, headers=headers)
	data = response.json()

	try:
		print(data)
		element = data["routes"][0]

		duration = '%.1f'%(int(element["duration"][:-1])/60)

		return duration
	except Exception as e:
		print(f"Error: {e}")
		return None, None, None

# -----------------------------------
# LOGGING
# -----------------------------------

def log_row(row):
	file_exists = os.path.isfile(DATA_FILE)

	with open(DATA_FILE, "a", newline="") as f:
		writer = csv.writer(f)

		if not file_exists:
			writer.writerow([
				"timestamp",
				"person",
				"direction",
				"origin",
				"destination",
				"transportation",
				"duration_minutes"
			])

		writer.writerow(row)

# -----------------------------------
# COMMUTE LOGIC
# -----------------------------------

def morning_commute():
	print(f"\n🌅 Morning run: {datetime.now()}")

	for city in CITIES:
		for work in WORK_LOCATIONS:
			def log_duration(methodOfTravel):
				duration = get_travel_time(CITIES[city], WORK_LOCATIONS[work], methodOfTravel)

				if duration:
					row = [
						datetime.now().astimezone(ZoneInfo("America/Los_Angeles")).isoformat(),
						"Lizzy" if work == "San Francisco, CA" else "Ben",
						"to_work",
						work,
						city,
						methodOfTravel,
						duration
					]

					log_row(row)

			if city != work:
				log_duration("DRIVE")
				if work == "San Francisco, CA":
					log_duration("TRANSIT")

def evening_commute():
	print(f"\n🌆 Evening run: {datetime.now()}")

	for city in CITIES:
		for work in WORK_LOCATIONS:
			def log_duration(methodOfTravel):
				duration = get_travel_time(WORK_LOCATIONS[work], CITIES[city], methodOfTravel)

				if duration:
					row = [
						datetime.now().astimezone(ZoneInfo("America/Los_Angeles")).isoformat(),
						"Lizzy" if work == "San Francisco, CA" else "Ben",
						"to_home",
						work,
						city,
						methodOfTravel,
						duration
					]

					log_row(row)

			if city != work:
				log_duration("DRIVE")
				if work == "San Francisco, CA":
					log_duration("TRANSIT")
			

# -----------------------------------
# SCHEDULE
# -----------------------------------

# Morning commute checks
schedule.every().day.at("08:00").do(morning_commute)
schedule.every().day.at("09:00").do(morning_commute)
schedule.every().day.at("10:00").do(morning_commute)

# Evening commute checks
schedule.every().day.at("18:00").do(evening_commute)
schedule.every().day.at("19:00").do(evening_commute)
schedule.every().day.at("20:00").do(evening_commute)
schedule.every().day.at("21:00").do(evening_commute)

# -----------------------------------
# LOOP
# -----------------------------------

if __name__ == "__main__":
	print("🚗 Commute tracker running...")

	morning_commute()

	while True:
		schedule.run_pending()
		time.sleep(30)