import constants
import json
import os
from datetime import datetime
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from random import random, randint


class VitaminDTracker:
    def __init__(self):
        self.load()

    def load(self):
        if os.path.exists("entries.json"):
            with open("entries.json") as file:
                self.entries = json.loads(file.read())
        else:
            self.entries = {}

        self.today = datetime.now().strftime("%d-%m-%Y")
        if self.today not in self.entries:
            self.entries[self.today] = {}

    def backup(self):
        with open("entries.json", "w") as file:
            file.write(json.dumps(self.entries, indent=4))

    def process_entry(self, log_entry, user_data):
        print("Processing entry:", log_entry)

        start_time = datetime.strptime(log_entry["start_time"], "%H:%M").time()
        end_time = datetime.strptime(log_entry["end_time"], "%H:%M").time()

        start_time_secs = (
            start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        )
        end_time_secs = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

        duration = abs(end_time_secs - start_time_secs)
        print(duration)

        vitamin_d = self.calculate_vitamin_d(
            log_entry["location"][1],
            log_entry["start_time"],
            duration,
            log_entry["body"],
            user_data.data["skin_type"],
            user_data.data["age"],
        )

        self.entries[self.today][log_entry["start_time"]] = {
            "duration": str(duration),
            "reading": str(vitamin_d),
            "location": log_entry["location"][0],
            "body": log_entry["body"],
        }

        self.backup()

    def get_last_7(self):
        return self.sorted_days()[-7:]

    def daily_total(self, day):
        total = 0
        for timestamp in self.entries[day]:
            total += int(self.entries[day][timestamp]["reading"])

        return total

    def add_entry(self, day, time, entry):
        if day not in self.entries:
            self.entries[day] = {}

        self.entries[day][time] = entry

    def sorted_days(self):
        return sorted(
            self.entries.keys(),
            key=lambda time_str: datetime.strptime(time_str, "%d-%m-%Y").time(),
        )

    def sorted_times(self, day):
        return sorted(
            self.entries[day].keys(),
            key=lambda time_str: datetime.strptime(time_str, "%H:%M").time(),
        )

    def convert_text_to_gps(self, text_address):
        base_url = "https://api.opencagedata.com/geocode/v1/json"
        params = {
            "q": text_address,
            "key": constants.ocd_key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["total_results"] > 0:
            location = data["results"][0]["geometry"]
            return location["lat"], location["lng"]
        else:
            print(f"Failed to find '{text_address}'!")
            return None

    def get_uvi_from_openmeteo(self, gps_coordinates):
        """
        Fetches uvi from openmeteo rest api.
        Returns UV-I max and UV-I max (clear sky) for next 7 days.

        """
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        params = {
            "latitude": gps_coordinates[0],
            "longitude": gps_coordinates[1],
            "daily": ["uv_index_max", "uv_index_clear_sky_max"],
            "timezone": "GMT",
        }
        responses = openmeteo.weather_api(constants.openmeteo_url, params=params)
        response = responses[0]
        daily = response.Daily()
        daily_uv_index_max = daily.Variables(0).ValuesAsNumpy()
        daily_uv_index_clear_sky_max = daily.Variables(1).ValuesAsNumpy()

        return daily_uv_index_max, daily_uv_index_clear_sky_max

    def compute_bsa(self, body, age):
        """
        Compute Body Surface area based on age and markers.
        """
        if age <= 1:
            age_group = "birth"
        elif 1 < age <= 4:
            age_group = "1-4"
        elif 4 < age <= 9:
            age_group = "5-9"
        elif 9 < age <= 14:
            age_group = "10-14"
        elif age == 15:
            age_group = "15"
        else:
            age_group = "adult"

        total_surface = 0
        for pos, value in body.items():
            if value:
                total_surface += constants.body_surface_area[age_group][pos]

        return total_surface / 100

    def calculate_vitamin_d(
        self, gps_coordinates, start_time, time_duration, body, skin_type, age
    ):
        # calculate body surface area (bsa)
        bsa = self.compute_bsa(body, age)

        # calculate minimal erythema dosage (med)
        med = constants.med[skin_type]

        # get today's maximum clearsky reading
        uvi = self.get_uvi_from_openmeteo(gps_coordinates)[1][0]

        # TODO: add deterioration based on time of day
        hour = int(start_time.split(":")[0])
        fractions = {
            8: 0.2,
            9: 0.5,
            10: 0.7,
            11: 0.9,
            12: 1,
            13: 0.9,
            14: 0.7,
            15: 0.5,
            16: 0.2,
        }

        if hour not in fractions:
            uvi = 0
        else:
            uvi *= fractions[hour]

        # calculate vitamin d
        print(
            f"calculating vitamin D: uvi={uvi}, time_duration={time_duration}, bsa={bsa}, med={med}"
        )
        vitamin_d = round((21120 * uvi * time_duration * bsa) / (40 * med))
        print(f"VitaminD={vitamin_d}")
        return vitamin_d

class UserData:
    def __init__(self):
        self.load_user_data()

    def load_user_data(self):
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r") as rfile:
                self.data = json.loads(rfile.read())
        else:
            self.data = None

    def save_user_data(self):
        with open("user_data.json", "w") as file:
            file.write(json.dumps(self.data, indent=4))


# schema = {
#     "<day>": {
#         "<time>": {
#             "duration": "",
#             "reading": "",
#             "location": "",
#             "body": {
#                 "head": False,
#                 "neck": False,
#                 "left_arm_upper": False,
#                 "left_arm_lower": False,
#                 "left_palm": False,
#                 "right_arm_upper": False,
#                 "right_arm_lower": False,
#                 "right_palm": False,
#                 "torso": False,
#                 "left_leg_upper": False,
#                 "left_leg_lower": False,
#                 "left_feet": False,
#                 "right_leg_upper": False,
#                 "right_leg_lower": False,
#                 "right_feet": False,
#             },
#         }
#     }
# }
