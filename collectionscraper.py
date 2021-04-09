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
			print("Misc retrieval error, likely a deleted Thing")
		else:
			file_list.append([thing_json['name'], thing_json['files_url']])
	for h in file_list:
		fixed_name = ''.join(i for i in h[0] if not i in bad_chars)
		#Handles two things with the same name
		if os.path.exists(fixed_name):
			print("Duplicate Thing name found, adding Dup suffix")
			fixed_name += " Dup"
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

#Begin main script

#Checks if script is being run directly with arguments and --auto flag, or to run interactively
interactive = True
if "--auto" in sys.argv:
	interactive = False
if len(sys.argv) < 3:
	#print("Not enough arguments!")
	author_name = input("Enter Author Name: ");
	coll_name = input("Enter collection name: ");
	#sys.exit()
else:
	if len(sys.argv) == 3:
		coll_name = sys.argv[2]
		author_name = sys.argv[1]
	elif len(sys.argv) == 4:
		coll_name = sys.argv[3]
		author_name = sys.argv[2]
base_url = "https://api.thingiverse.com"

#Set user_token to own Thingiverse app token if needed (if mine goes down for instance)
user_token = '7e6dfd8711b4c5af4773ac827e1249e3'

app_token = 'Bearer ' + user_token
headers = {
	"Accept": "application/json",
	"authorization": app_token
}
#Pagination count, set below
page_count = 1

params = {}
#Removes special characters from collection name before directory creation (especially for /)
clean_name = ''.join(i for i in coll_name if not i in bad_chars)

if os.path.exists(clean_name):
	if interactive:
		user_ans = input("Directory exists, delete? (y/n): ")
		if user_ans.lower() == "y" or user_ans.lower() == "yes":
			shutil.rmtree(clean_name, ignore_errors=True)
		else:
			user_ans = input("Alternate dir name: ")
			user_ans = ''.join(i for i in user_ans if not i in bad_chars)
			while os.path.exists(user_ans):
				print("Already exists?")
				user_ans = input("Alternate dir name: ")
				user_ans = ''.join(i for i in user_ans if not i in bad_chars)
			clean_name = user_ans
	else:
		shutil.rmtree(clean_name, ignore_errors=True)
os.mkdir(clean_name)
os.chdir(clean_name)

#Gets all collections from a given user (might only support users with <= 30 collections, pagination might be needed here too, would be trickier)
response = requests.get(base_url + "/users/" + author_name + "/collections/{$all}", headers = headers, data=json.dumps(params)) 
j = response.json()

#Sets to negative value, will be made positive if eventually found below
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
	print("Invalid collection info, not found (check spelling!)")
	os.chdir("..")
	shutil.rmtree(clean_name, ignore_errors=True)
	sys.exit()