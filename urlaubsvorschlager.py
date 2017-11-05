#!/usr/bin/env python3

import sys
import os
import csv
import pathlib
import numpy as np
import scipy
import scipy.spatial
import time
import pickle
import math

# eucl_dist = scipy.spatial.distance.euclidean

def eucl_dist(a, b):
	return np.sqrt(np.sum((other_user_checkins_lat_lngs - lat_lng)**2, axis=1))

DIRECTORY = "./gowalla/loc-gowalla_totalCheckins.txt/"
FILE_NAME = DIRECTORY+"data"
SIMILARITY_FILE_NAME = DIRECTORY+"similarities"
PRINT_STEP_PARSE = 10000
MAX_STEPS_PARSE = 100000
PRINT_STEP_SIMILARITIES = 10
USERS_TO_USE_FOR_SUGGESTIONS = 100

user_id = int(sys.argv[1])

def pickle_something(file_name, function):
	def inner_function(*args):
		if not pathlib.Path(file_name+".pickle").is_file() or os.stat(file_name+".pickle").st_size <= 0:
			returned_stuff = function(*args)
			with open(file_name+".pickle", "wb") as f_pickle:
				print("Pickling data:", file_name+".pickle")
				pickle.dump(returned_stuff, f_pickle)
		else:
			print("Reading pickled data:", file_name+".pickle")
			with open(file_name+".pickle", "rb") as f_pickle:
				returned_stuff = pickle.load(f_pickle)
		print("Done with pickle stuff:", file_name+".pickle")
		return returned_stuff
	return inner_function

def parse_file_raw(file_name):
	print("Creating training data from scratch.")
	user_to_checkin = {}
	user_to_medoid = {}
	with open(file_name) as csvfile:
		checkins = csv.reader(csvfile, delimiter="\t")
		for index, row in enumerate(checkins):
			if index >= MAX_STEPS_PARSE:
				break
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
			if index % PRINT_STEP_PARSE == 0:
				print("Parsed", index, "lines.")
			# print("Finished building dictionary.")
	print("Calculating users' medoids.")

	for user_id in user_to_checkin:
		user_to_medoid[user_id] = calculate_medoid_of_user(user_id, user_to_checkin)
	print("Finished calculating medoids.")
	return user_to_checkin, user_to_medoid

parse_file = pickle_something(FILE_NAME, parse_file_raw)

def calculate_similarity_to_each_user_raw(user_id, user_to_checkin, user_to_medoid):
	print("Creating similarities from scratch.")
	all_user_ids = list(user_to_checkin.keys())
	# print("user_id", type(user_id))
	# print("all_user_ids", type(all_user_ids[0]))
	all_user_ids.remove(user_id)
	# all_user_ids = np.array(all_user_ids)

	# TODO: Vectorizing would be nicer but it doesn't allow you to view the progress
	# calculate_similarity_vectorized = np.vectorize(calculate_similarity_between_two_users)
	# print("Calculating similarities.")
	# similarities = calculate_similarity_vectorized(user_id, all_user_ids, user_to_checkin, user_to_medoid)

	similarities = []
	last_debug_timer = time.time()
	for user_index, other_user_id in enumerate(all_user_ids):
		if user_index % PRINT_STEP_SIMILARITIES == 0 and user_index > 0:
			new_debug_timer = time.time()
			print("Processed", user_index, "other users, speed:", PRINT_STEP_SIMILARITIES/(new_debug_timer-last_debug_timer), "users/second")
			last_debug_timer = new_debug_timer
		similarities.append(calculate_similarity_between_two_users(user_id, other_user_id, user_to_checkin, user_to_medoid))

	print("Calculated similarities.")
	sorted_indices = similarities.argsort()
	print("Sorted similarities.")

	all_user_ids, similarities = all_user_ids[sorted_indices], similarities[sorted_indices]
	return all_user_ids[sorted_indices], similarities[sorted_indices]

calculate_similarity_to_each_user = pickle_something(SIMILARITY_FILE_NAME+"-"+str(user_id), calculate_similarity_to_each_user_raw)

# TODO: write function that takes the first n (e.g. 1000) best other users.
# Then it uses like 100 medoid clustering on their checkins and returns the 10 ones with the least variance.
# Write a flask webserver and a Facebook app integration.
# When a Facebook user connects, his data is added to the dataset, and then the dissimilarities etc are calculated.

def calculate_similarity_between_two_users(user_id, other_user_id, user_to_checkin, user_to_medoid):
	user_checkins = user_to_checkin[user_id]
	other_user_checkins = user_to_checkin[other_user_id]
	user_medoid = np.array(user_to_medoid[user_id])
	other_user_medoid = np.array(user_to_medoid[other_user_id])

	user_checkins_lat_lngs = np.array(user_checkins[0])
	print("user_checkins_lat_lngs.shape", user_checkins_lat_lngs.shape)
	other_user_checkins_lat_lngs = np.array(other_user_checkins[0])
	print("other_user_checkins_lat_lngs.shape", other_user_checkins_lat_lngs.shape)

	# FIXME: I guess you can leave out all the sqrts
	differences_places = np.sqrt(np.sum((np.expand_dims(user_checkins_lat_lngs, axis=1) - np.expand_dims(other_user_checkins_lat_lngs, axis=0))**2, axis=2))
	print("differences_places.shape", differences_places.shape)

	print("user_checkins_lat_lngs.shape", user_checkins_lat_lngs.shape)
	differences_homes_user = np.sqrt(np.sum((user_checkins_lat_lngs - user_medoid)**2, axis=1))
	print("differences_homes_user.shape", differences_homes_user.shape)
	print("other_user_checkins_lat_lngs.shape", other_user_checkins_lat_lngs.shape)
	differences_homes_other_user = np.sqrt(np.sum((other_user_checkins_lat_lngs - other_user_medoid)**2, axis=1))
	print("differences_homes_other_user.shape", differences_homes_other_user.shape)
	differences_homes = np.multiply(np.expand_dims(differences_homes_user, axis=1), np.expand_dims(differences_homes_other_user, axis=0))
	print("differences_homes.shape", differences_homes.shape)

	assert(differences_places.shape == differences_homes.shape)
	differences = np.divide(differences_places, differences_homes)
	print("differences.shape", differences.shape)
	minimum_difference_for_each_location_of_the_user = differences.min(axis=0)
	# FIXME: Dimensionen sind irgendwie vertauscht...
	if minimum_difference_for_each_location_of_the_user.shape[0] != user_checkins_lat_lngs.shape[0]:
		print(minimum_difference_for_each_location_of_the_user.shape, user_checkins_lat_lngs.shape)
	assert(minimum_difference_for_each_location_of_the_user.shape[0] == user_checkins_lat_lngs.shape[0])

	total_difference = np.sum(minimum_difference_for_each_location_of_the_user)/user_checkins_lat_lngs.shape[0]
	return total_difference

def calculate_medoid_of_user(user_id, user_to_checkin):
	checkin_array = np.array(user_to_checkin[user_id][0])
	distance_matrix = scipy.spatial.distance.pdist(checkin_array)
	## Whether you use axis 0 or 1 doesn't matter as the matrix is quadratic
	medoid_index = np.argmin(np.sum(distance_matrix, axis=0))
	return checkin_array[medoid_index]

user_to_checkin, user_to_medoid = parse_file(FILE_NAME)
print("Read", len(user_to_checkin.keys()), "users.")
print("Calculating Urlaubsvorschlag for user", user_id)
users_sorted_by_similarity, sorted_similarities = calculate_similarity_to_each_user(user_id, user_to_checkin, user_to_medoid)
best_other_users = users_sorted_by_similarity[:USERS_TO_USE_FOR_SUGGESTIONS]
