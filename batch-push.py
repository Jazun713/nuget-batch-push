#!/usr/local/bin/python3

import os
import re
import shlex
import subprocess
from multiprocessing.pool import ThreadPool
from collections import OrderedDict


root_path = os.environ['NuGetPath']
hostUrl = os.environ['MyGetUrl']
apiKey = os.environ['MyGetApiKey']
pattern = "*.nupkg"


def call_proc(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print(stdout.decode('ascii'))
    return stdout, stderr


def scan_dir(_dir):
    print(_dir)
    for entry in os.scandir(_dir):
        if entry.name.endswith('.nupkg') and entry.is_file():
            yield entry.name


def subdirs(path):
    for entry in os.scandir(path):
        if not entry.name.startswith('.') and entry.is_dir():
            print(entry.name)
            yield entry.name


gen = subdirs(root_path)
pool = ThreadPool(8)
results = []


for dir_name in gen:
    dir_name = root_path + dir_name
    file_gen = list(scan_dir(dir_name))
    file_gen.sort()
    od = OrderedDict()
    for file_name in file_gen:
        match = re.compile('\.(?=\d)').split(file_name)
        match = list(filter(None, match))
        head = match.pop(0)
        tail = '.'.join(match)
        od.setdefault(head, []).append(tail)
    for key, value in od.items():
        value = value[-1]
        file_path = dir_name + "/" + key + "." + value
        print("Queuing file: " + file_path)
        args = "push " + file_path + " " + apiKey + " -s " + hostUrl
        results.append(pool.apply_async(call_proc, ("nuget " + args,)))


pool.close()
pool.join()
for result in results:
    out, err = result.get()
    print("out: {} err: {}".format(out, err))
