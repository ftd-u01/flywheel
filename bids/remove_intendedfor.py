#!/usr/bin/env python

import csv
import json
import os
import sys
from textwrap import dedent

def remove_intendedfor(fmap_sidecar_paths):
    for fidx in range(len(fmap_sidecar_paths)):
        fi = open(fmap_sidecar_paths[fidx], 'r')
        fmap_json = json.load(fi)
        fi.close()
        # If IntendedFor key is present, remove it
        if 'IntendedFor' in fmap_json:
            del fmap_json['IntendedFor']
        fo = open(fmap_sidecar_paths[fidx], 'w')
        json.dump(fmap_json, fo, indent=2, sort_keys=True)
        fo.close()

if len(sys.argv) == 1:
   print(dedent(sys.argv[0] + " <bids dataset dir> <sessions>\n" +
         '''
            This script will remove the IntendedFor field from all files under fmap/ in a session.
            It is intended for use when the IntendedFor is incorrect in a way that breaks the
            BIDSLayout.

            sessions is a csv file with two columns: <subject label>,<session label>

            We assume a sub-Subject/ses-Session/fmap/ directory structure.
         '''))
   sys.exit(1)


sessions_to_process = []

if len(sys.argv) > 2:
    with open(sys.argv[2], newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            sessions_to_process.append(row)
else:
    print ("Sessions file is required")
    sys.exit(1)

# Get all fmap json files
for sess in sessions_to_process:
    fmap_sidecar_paths = []
    fmap_dir = os.path.join(sys.argv[1], 'sub-'+sess[0], 'ses-'+sess[1], 'fmap')
    for root, dirs, files in os.walk(fmap_dir):
        for file in files:
            if file.endswith(".json"):
                fmap_sidecar_paths.append(os.path.join(root, file))

    if len(fmap_sidecar_paths) > 0:
        remove_intendedfor(fmap_sidecar_paths)
