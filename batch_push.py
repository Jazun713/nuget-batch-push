#!/usr/local/bin/python3
import fnmatch
import os
import re
import subprocess
import shutil
import shlex
import multiprocessing
from multiprocessing.pool import ThreadPool

rootPath = "/path/to/server"
pattern = "*.nupkg"
hostUrl = "https://internal/api/v2/package"
apiKey = "apikey-here"

def call_proc(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print(out.decode('ascii'))
    return (out, err)

_prefix = []
results = []
pool = ThreadPool(8)

for root, dirs, files in os.walk(rootPath):
  files.sort()
  for filename in fnmatch.filter(files, pattern):
    filePath = os.path.join(root, filename)
    filePrefix = re.compile(r'\w+\.\w+(?=\.)') #change pattern to match your filenames
    matchPrefix = filePrefix.search(filename)
    _prefix.append((matchPrefix.group(), filePath))

d = dict(_prefix)
v = d.values()
for item in v:
  args = "push " + item + " " + apiKey + " -s " + hostUrl
  results.append(pool.apply_async(call_proc, ("nuget " + args,)))

pool.close()
pool.join()
for result in results:
    out, err = result.get()
    print("out: {} err: {}".format(out, err)) 
