#!/usr/local/bin/python3

import os
import requests

url = 'http://wjv-docker01:8081/artifactory/nuget-internal'
auth = ('jasande', 'AKCp2V6nXcRSQu7sHjWhRLAGqkLSNarDHAaKhxXw7aaws6ZtprN1T9KTyrPp9NDrrP2dUf5qG')
headers = {'X-Explode-Archive': 'True'}

def scan_zip(_dir):
  for entry in os.scandir(_dir):
    if entry.name.endswith('.zip') and entry.is_file():
      yield entry.name

def subdirs(path):
  for entry in os.scandir(path):
    if not entry.name.startswith('.') and entry.is_dir():
      print(entry.name)
      yield entry.name

cwd = os.getcwd()
archive_dir = os.path.join(cwd, "Archive")
gen = list(scan_zip(archive_dir))
for file_name in gen:
  localfilepath = os.path.abspath(os.path.join(archive_dir, file_name))
  base_name = file_name.split('.', 1)
  print("zip file name is: %s" % file_name)
  url_new = url + '/' + base_name[0] + '/' + file_name
  print("url is: %s" % url_new)

  with open(localfilepath, 'rb') as zip_file:
    files = {'file': (file_name, zip_file, 'application/zip')}
    resp = requests.put(url_new, auth=auth, headers=headers, data=zip_file)
  print(resp.status_code)

#curl -u jasande:AKCp2V6nXcRSQu7sHjWhRLAGqkLSNarDHAaKhxXw7aaws6ZtprN1T9KTyrPp9NDrrP2dUf5qG -H "X-Explode-Archive: True" --upload-file  /Users/jasande/code/nuget-batch-push/Archive/update-readme.zip http://wjv-docker01:8081/artifactory/nuget-internal/ExtendHealth/update-readme/update-readme.zip
