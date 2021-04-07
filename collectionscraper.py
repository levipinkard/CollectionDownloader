import requests
import shutil
import math
import sys
import os
import json

#Used for cleaning up Thing names for folders
bad_chars = ['/', ':', '!', "*"]


#Given a list of Things, download the files of each one
def get_all_files(thing_list):
	file_list = []
	for i in thing_list:
		thing_resp = requests.get(base_url + "/things/" + str(i) + "/", headers = headers, data=json.dumps(params))
		thing_json = thing_resp.json()
		if 'error' in thing_json:
			print("Found deleted Object")
		else:
			file_list.append([thing_json['name'], thing_json['files_url']])
	for h in file_list:
		fixed_name = ''.join(i for i in h[0] if not i in bad_chars)
		os.mkdir(fixed_name)
		os.chdir(fixed_name)
		file_resp = requests.get(h[1], headers = headers, data=json.dumps(params))
		file_json = file_resp.json()
		print("Downloading " + fixed_name)
		for k in file_json:
			#Actually writes all files from current Thing
			file_download = requests.get(k['download_url'], headers = headers, data=json.dumps(params))
			open(k['name'], 'wb').write(file_download.content)
		os.chdir("..")

#Begin script

#Checks if script is being run directly with arguments, or to run interactively
if len(sys.argv) != 3:
	#print("Not enough arguments!")
	author_name = input("Enter Author Name: ");
	coll_name = input("Enter collection name: ");
	#sys.exit()
else:
	coll_name = sys.argv[2]
	author_name = sys.argv[1]

base_url = "https://api.thingiverse.com"
app_token = 'Bearer 7e6dfd8711b4c5af4773ac827e1249e3'
headers = {
	"Accept": "application/json",
	"authorization": app_token
}
#Pagination count, set below
page_count = 1
params = {}
shutil.rmtree(coll_name, ignore_errors=True)
os.mkdir(coll_name)
os.chdir(coll_name)

#Gets all collections from a given user (might only support users with <= 30 collections, pagination might be needed here too, would be trickier)
response = requests.get(base_url + "/users/" + author_name + "/collections/{$all}", headers = headers, data=json.dumps(params)) 
j = response.json()

coll_id = -1

#Searches for a given collection name
for i in j:
	if i['name'].lower() == coll_name.lower():
		coll_id = i['id']
		#Updates required pagination
		page_count = math.ceil(i['count'] / 30)

#coll_id will be changed from default if and only if the proper collection is found
if coll_id != -1:
	print("Found collection!")
	id_list = []
	for x in range(0, 2 + page_count):
		coll_resp = requests.get(base_url + "/collections/" + str(coll_id) + "/things?page=" + str(x+1), headers = headers, params=params)
		coll = coll_resp.json()
		#Adds IDs for all things in the given collection
		for o in coll:
			id_list.append(o['id'])
	#Removes duplicates in the case of accidentally counting the same page twice
	clean_list = []
	for i in id_list:
		if i not in clean_list:
			clean_list.append(i)
	print("Downloading " + str(len(clean_list)) + " objects")
	get_all_files(clean_list)
else:
	print("Invalid collection info, not found")
	os.chdir("..")
	shutil.rmtree(coll_name, ignore_errors=True)
	sys.exit()