import requests
import shutil
import math
import sys
import os
import json
bad_chars = ['/', ':', '!', "*"]

def get_all_files(thing_list):
	file_list = []
	for i in thing_list:
		thing_resp = requests.get(base_url + "/things/" + str(i) + "/", headers = headers, data=json.dumps(params))
		thing_json = thing_resp.json()
		#print(json.dumps(thing_json, indent=4))
		#sys.stdout.flush()
		if 'error' in thing_json:
			print("Found deleted Object")
		else:
			file_list.append([thing_json['name'], thing_json['files_url']])
		#print(thing_json['files_url'])
	#print(file_list)
	for h in file_list:
		fixed_name = ''.join(i for i in h[0] if not i in bad_chars)
		os.mkdir(fixed_name)
		os.chdir(fixed_name)
		file_resp = requests.get(h[1], headers = headers, data=json.dumps(params))
		file_json = file_resp.json()
		#print(json.dumps(file_json, indent=4))
		print("Downloading " + fixed_name)
		for k in file_json:
			#print(json.dumps(k, indent=4))
			file_download = requests.get(k['download_url'], headers = headers, data=json.dumps(params))
			open(k['name'], 'wb').write(file_download.content)
		os.chdir("..")


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
#r = requests.post("https://www.thingiverse.com/login/oauth/access_token", data=json.dumps(authenticate), verify=False)
headers = {
	"Accept": "application/json",
	"authorization": app_token
}
page_count = 1
params = {}
shutil.rmtree(coll_name, ignore_errors=True)
os.mkdir(coll_name)
os.chdir(coll_name)
#print(json.dumps(j, indent=4))
response = requests.get(base_url + "/users/" + author_name + "/collections/{$all}", headers = headers, data=json.dumps(params)) 
j = response.json()
coll_id = -1
#print(json.dumps(j, indent=4))
for i in j:
	if i['name'].lower() == coll_name.lower():
		#print(i['id'])
		coll_id = i['id']
		page_count = math.ceil(i['count'] / 30)
		#print(page_count)
if coll_id != -1:
	print("Found collection!")
	id_list = []
	for x in range(0, 2 + page_count):
		params = {
			'page' : x
		}
		coll_resp = requests.get(base_url + "/collections/" + str(coll_id) + "/things?page=" + str(x+1), headers = headers, params=params)
		coll = coll_resp.json()
		#print(json.dumps(coll, indent=4))
		#print(len(coll))
		for o in coll:
			id_list.append(o['id'])
		#print(id_list)
		#test_resp = requests.get(base_url + "/things/3389727/files", headers = headers, data=json.dumps(params))
		#open('testfile', 'wb').write(test_resp.content)
		#test_json = test_resp.json()
		#print(json.dumps(test_json, indent=4))
	clean_list = []
	for i in id_list:
		if i not in clean_list:
			clean_list.append(i)
	print("Downloading " + str(len(clean_list)) + " objects")
	get_all_files(clean_list)
else:
	print("Invalid collection info, not found")
	sys.exit()

#print(j[0]['id'])