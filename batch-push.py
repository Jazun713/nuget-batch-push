#!/usr/local/bin/python3

import os
import re
import shlex
import subprocess
import shutil
from multiprocessing.pool import ThreadPool
from collections import OrderedDict
from os.path import expanduser


root_path = os.environ.get('NuGetPath', '/mnt/ntserver/')
hostUrl = os.environ.get('NugetServerUrl', 'http://wjv-docker01:8081/artifactory/api/nuget/nuget-internal')
apiKey = os.environ.get('NugetApiKey', '')
pattern = "*.nupkg"


def scan_dir(_dir):
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
        module = key.split('.', 1)
        try:
            moduletail = module[1]
        except IndexError:
            moduletail = module[0]
        if moduletail == module[0]:
            orgdir = os.path.expanduser('~/ExtendHealth')
        else:
            orgdir = os.path.expanduser('~/ExtendHealth/' + module[0])
        moduledir = orgdir + "/" + moduletail
        modulefile = moduledir + "/" + key + "." + value
        os.makedirs(moduledir, exist_ok=True)
        if os.path.isfile(modulefile):
            print("    File %s exists. Skipping..." % modulefile)
        else:
            print("    File %s does not exist. Copying..." % modulefile)
            pool.apply_async(shutil.copy2(file_path, moduledir))


local_path = os.path.expanduser('~/ExtendHealth')
cwd = os.getcwd()
base_dir = os.path.join(cwd, "Archive")
os.makedirs(base_dir, exist_ok=True)
gen2 = subdirs(local_path)
for dir_name in gen2:
    root_dir = os.path.join(local_path, dir_name)
    print("    Archiving %s please wait..." % dir_name)
    pool.apply_async(shutil.make_archive(os.path.join(base_dir, dir_name), 'zip', root_dir))


pool.close()
pool.join()
