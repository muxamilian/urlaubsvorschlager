#!/usr/bin/env python3

import csv
import pathlib
import numpy as np
import scipy as sp

FILE_NAME = "./gowalla/loc-gowalla_totalCheckins.txt/data"
PRINT_STEP = 10000

def parse_file(file_name):
	if not pathlib.Path(FILE_NAME+".pickle").is_file():
		print("Creating training data from scratch.")
		user_to_checkin = {}
		with open(FILE_NAME) as csvfile:
			checkins = csv.reader(csvfile, delimiter="\t")
			index = 0
			for row in checkins:
				user_id = int(row[0])
				lat_lng = (float(row[2]), float(row[3]))
				month = time.strptime(row[1], "%Y-%m-%dT%H:%M:%SZ").tm_mon
				# location_id = row[4] # We don't need this currently
				if not user_id in user_to_checkin:
					user_to_checkin[user_id] = [(lat_lng, month)]
				else:
					user_to_checkin[user_id].append((lat_lng, month))

				index += 1
				print("Parsed", index, "lines.")
		print("Finished building dictionary.")
	else: 
		print("Reading pickled data.")
		with open(FILE_NAME+".pickle", "rb") as f_pickle:
			user_to_checkin = pickle.load(f_pickle)
	return user_to_checkin
	
user_to_checkin = parse_file(FILE_NAME)

def get_similarity_to_each_user(user_id, user_to_checkin):

def calculate_medoid_of_user(user_id):
	return 
