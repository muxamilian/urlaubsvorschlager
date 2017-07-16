#!/usr/bin/env python3

import csv
import pathlib
import numpy as np
import scipy
import scipy.spatial

eucl_dist = scipy.spatial.distance.euclidean

FILE_NAME = "./gowalla/loc-gowalla_totalCheckins.txt/data"
PRINT_STEP = 10000

def parse_file(file_name):
	if not pathlib.Path(file_name+".pickle").is_file():
		print("Creating training data from scratch.")
		user_to_checkin = {}
		user_to_medoid = {}
		with open(file_name) as csvfile:
			checkins = csv.reader(csvfile, delimiter="\t")
			index = 0
			for row in checkins:
				user_id = int(row[0])
				lat_lng = np.array([float(row[2]), float(row[3])])
				month = time.strptime(row[1], "%Y-%m-%dT%H:%M:%SZ").tm_mon
				## We don't need this currently
				# location_id = row[4]
				if not user_id in user_to_checkin:
					user_to_checkin[user_id] = ([lat_lng], [month])
				else:
					user_to_checkin[user_id][0].append(lat_lng)
					user_to_checkin[user_id][1].append(month)

				index += 1
				# if index % PRINT_STEP == 0:
				# 	print("Parsed", index, "lines.")
				print("Finished building dictionary.")
		print("Calculating users' medoids.")
		
		for user_id in user_to_checkin:
			user_to_medoid[user_id] = calculate_medoid_of_user(user_id, user_to_checkin)
		printed("Finished calculating medoids.")

		with open(file_name+".pickle", "wb") as f_pickle:
			print("Pickling data.")
			pickle.dump((user_to_checkin, user_to_medoid), f_pickle)
	else: 
		print("Reading pickled data.")
		with open(file_name+".pickle", "rb") as f_pickle:
			user_to_checkin, user_to_medoid = pickle.load(f_pickle)
	return user_to_checkin, user_to_medoid
	
def calculate_similarity_to_each_user(user_id, user_to_checkin, user_to_medoid):
	all_user_ids = list(user_to_checkin.keys())
	all_user_ids.remove(user_id)
	all_user_ids = np.array(all_user_ids)

	calculate_similarity_vectorized = np.vectorize(calculate_medoid_of_user)
	similarities = calculate_similarity_vectorized(user_id, all_user_ids, user_to_checkin, user_to_medoid)
	sorted_indices = similarities.argsort()
	return all_user_ids[sorted_indices], similarities[sorted_indices]

# TODO: write function that takes the first n (e.g. 1000) best other users. 
# Then it uses like 100 medoid clustering on their checkins and returns the 10 ones with the least variance. 
# Write a flask webserver and a Facebook app integration. 
# When a Facebook user connects, his data is added to the dataset, and then the dissimilarities etc are calculated. 

def calculate_similarity_between_two_users(user_id, other_user_id, user_to_checkin, user_to_medoid):
	user_ids = 
	user_checkins = user_to_checkin(user_id)
	other_user_checkins = user_to_checkin(other_user_id)
	user_medoid = user_to_medoid[user_id]
	other_user_medoid = user_to_medoid[other_user_id]

	total_difference = 0.0
	for lat_lng, month in zip(user_checkins[0], other_user_checkins[1]):
		# FIXME: So distance gets infinite if comparing users where one doesn't have any checkins
		partial_difference = float("inf")
		for other_lat_lng, other_month in zip(other_user_checkins[0], other_user_checkins[1]):
			# TODO: For now I don't consider the distance in month. You would need a multiplier to weigh the two distance components;
			# so one parameter alpha that you multipyl with the distance in months. 
			distance = eucl_dist(lat_lng, other_lat_lng)# + eucl_dist(month, other_month)
			distance_from_home = eucl_dist(lat_lng, user_medoid) * eucl_dist(other_lat_lng, other_user_medoid)
			score = distance/distance_from_home
			if score < partial_difference:
				partial_difference = score
		total_difference += partial_difference
	return total_difference / (len(user_checkins[0]) * len(other_user_checkins[0]))

def calculate_medoid_of_user(user_id, user_to_checkin):
	checkin_array = np.array(user_to_checkin[user_id])
	distance_matrix = scipy.spatial.distance.pdist(checkin_array)
	## Whether you use axis 0 or 1 doesn't matter as the matrix is quadratic
	medoid_index = np.argmin(np.sum(distance_matrix, axis=0))
	return checkin_array[medoid_index]

user_to_checkin = parse_file(FILE_NAME)
