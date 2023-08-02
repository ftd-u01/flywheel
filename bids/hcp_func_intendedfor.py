#!/usr/bin/env python

import csv
import json
import os
import sys
from bids import BIDSLayout
from textwrap import dedent

# Returns true if we can associate all imaging data with a field map
def intendFmaps(fmap_sidecar_paths, image_intendedfor_paths):
    if (len(image_intendedfor_paths) == 0):
        # No BOLD data for this run
        return False
    # Should be two fmaps, with reverse polarity (which we don't check here directly, but check
    # there's two). Polarity should be correct if there are two fmaps with same run- number.
    if (len(fmap_sidecar_paths) != 2):
        return False

    for fidx in range(0,2):
        fi = open(fmap_sidecar_paths[fidx], 'r')
        fmap_json = json.load(fi)
        fi.close()
        fmap_json['IntendedFor'] = image_intendedfor_paths
        fo = open(fmap_sidecar_paths[fidx], 'w')
        json.dump(fmap_json, fo, indent=2, sort_keys=True)
        fo.close()

    return True

if len(sys.argv) == 1:
   print(dedent(sys.argv[0] + " <bids dataset dir> [sessions]\n" +
         '''
         Finds func volumes to associate with fmaps, and updates fmap sidecars to include
         IntendedFor.

         Assumes bold run-[1,2] goes with fmaps run-[1,2]. fmap run-3 is for task only

         Optional session list in the format sub,ses on each line, where sub-\${sub}/ses-\${ses} exist
         '''))
   sys.exit(1)

layout = BIDSLayout(sys.argv[1], validate=True)

qc_header = 'subject,session,task,run,dir,suffix,relpath,fmap,error'

print(qc_header)

sessions_to_process = []

if len(sys.argv) > 2:
    with open(sys.argv[2], newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            sessions_to_process.append(row)
else:
    for subj in layout.get_subjects():
        for sess in layout.get(subject=subj, return_type='id', target='session'):
            sessions_to_process.append([subj, sess])

for elem in sessions_to_process:
    subj=elem[0]
    sess=elem[1]
    # fmaps should exist in AP / PA pairs, run-1 for rest run-1, run-2 for rest run-2, run-3 for
    # WM and GAMBLING

    # rest runs should be 1,2 but might be more if reacquired
    # task should not have run data, unless data reacquired
    # task fmap assignment should be fairly easy because they all go to fmap run 3.
    #
    # rest assignment gets tricky if there are multiple runs, best solved manually
    # These variables are lists of run numbers
    rest_runs = layout.get(subject=subj, session=sess, task='rest', datatype='func', target = 'run', return_type='id')
    fmap_runs = layout.get(subject=subj, session=sess, datatype='fmap', target = 'run', return_type='id')


    # rf bold data, list of images
    rf_bold_data = layout.get(subject=subj, session=sess, datatype='func', task='rest', extension='nii.gz')

    # tf bold data, list of images
    tf_bold_data = layout.get(subject=subj, session=sess, datatype='func', regex_search=True, task='(gambling|WM)', extension='nii.gz')

    # Everything - only used in case of error to print out everything
    all_bold_data = layout.get(subject=subj, session=sess, datatype='func', extension='nii.gz')

    if len(fmap_runs) == 0:
        print(f"{subj},{sess},NA,NA,NA,NA,NA,False,No fmap data")
        continue
    if len(rest_runs) == 0 and len(tf_bold_data) == 0:
        print(f"{subj},{sess},NA,NA,NA,NA,NA,False,No fmri data")
        continue

    # Special case: no run numbers on rfmri because there's only one run
    if len(rest_runs) == 0:
        if len(fmap_runs) > 0:
            # Pretty unlikely case where rfmri didn't finish but session got as far as the second field maps
            fmap_sidecar_bids = layout.get(subject=subj, session=sess, run="1", datatype='fmap', extension='json')
        else:
            # no run number for bold or fmap
            fmap_sidecar_bids = layout.get(subject=subj, session=sess, datatype='fmap', extension='json')
        fmap_sidecar_paths = [file.path for file in fmap_sidecar_bids]

        # bold paths in the intendedfor have to be relative to the subject dir
        rf_bold_intendedfor_paths = [file.relpath.replace(f'sub-{subj}/', '') for file in rf_bold_data]
        fmaps_assigned = intendFmaps(fmap_sidecar_paths, rf_bold_intendedfor_paths)
        for im in rf_bold_data:
            ent = im.entities
            print(f"{ent['subject']},{ent['session']},{ent['task']},NA,{ent['direction']},{ent['suffix']},{im.relpath},{fmaps_assigned},None")
        continue

    # Having got here, we know run numbers exist, so check all data has a run- number
    for im in rf_bold_data:
        ent = im.entities
        if not 'run' in ent:
            # don't do anything for a session if the rfmri curation is bad
            for im in all_bold_data:
                ent = im.entities
                try:
                    run = ent['run']
                except KeyError:
                    run = "NA"
                print(f"{ent['subject']},{ent['session']},{ent['task']},{run},{ent['direction']},"
                        f"{ent['suffix']},{im.relpath},False,Multiple rfmri but some missing run numbers")
            continue

    # If there's extra field maps, need to look at data to decide which to use
    if len(fmap_runs) > 3:
        # Don't do anything to the data in this case - require manual intervention
        for im in all_bold_data:
            ent = im.entities
        try:
            run = ent['run']
        except KeyError:
            run = "NA"
        print(f"{ent['subject']},{ent['session']},{ent['task']},{run},{ent['direction']},"
                    f"{ent['suffix']},{im.relpath},False,Extra fmap pairs")
        continue

    # This happens if rfmri is re-acquired. Need to remove partial scans to get the mapping correct
    if len(rest_runs) > 2 or len(fmap_runs) < len(rest_runs):
        # Don't do anything to the data in this case - require manual intervention
        for im in all_bold_data:
            ent = im.entities
            try:
                run = ent['run']
            except KeyError:
                run = "NA"
                print(f"{ent['subject']},{ent['session']},{ent['task']},{run},{ent['direction']},"
                      f"{ent['suffix']},{im.relpath},False,Extra func or too few fmaps")
        continue

    # The usual case is two runs of rest fmri with corresponding fmaps
    for rfRun in rest_runs:
        fmap_sidecar_bids = layout.get(subject=subj, session=sess, run=str(rfRun), datatype='fmap', extension='json')
        fmap_sidecar_paths = [file.path for file in fmap_sidecar_bids]

        # bold data
        rf_bold_data_single_run = layout.get(subject=subj, session=sess, datatype='func', task='rest', run=str(rfRun), extension='nii.gz')
        # bold paths in the intendedfor have to be relative to the subject dir
        rf_bold_intendedfor_paths = [file.relpath.replace(f'sub-{subj}/', '') for file in rf_bold_data_single_run]
        fmaps_assigned = intendFmaps(fmap_sidecar_paths, rf_bold_intendedfor_paths)
        for im in rf_bold_data_single_run:
            ent = im.entities
        try:
            run = ent['run']
        except KeyError:
            run = "NA"
        print(f"{ent['subject']},{ent['session']},{ent['task']},{ent['run']},{ent['direction']},{ent['suffix']},{im.relpath},{fmaps_assigned},None")

    # Now task - there may be multiple runs, but not more field maps
    # Only use fmap run-3 for task

    # First check for run numbers - the length of these are zero if there's no run- keys at all
    # Either none of the data should have run- or all of it should
    task_gambling_runs = layout.get(subject=subj, session=sess, datatype='func', target = 'run', return_type='id', task='gambling')
    task_wm_runs = layout.get(subject=subj, session=sess, datatype='func', target = 'run', return_type='id', task='WM')

    missing_tf_run_numbers = False

    if len(task_gambling_runs) > 0:
        # If there are run numbers, check all scans have them
        tf_gambling_data = layout.get(subject=subj, session=sess, datatype='func', task='gambling', extension='nii.gz')
        for im in tf_gambling_data:
            ent = im.entities
            if not 'run' in ent:
                missing_tf_run_numbers = True

    if len(task_wm_runs) > 0:
        # If there are run numbers, check all scans have them
        tf_wm_data = layout.get(subject=subj, session=sess, datatype='func', task='WM', extension='nii.gz')
        for im in tf_wm_data:
            ent = im.entities
            if not 'run' in ent:
                missing_tf_run_numbers = True

    if missing_tf_run_numbers:
        for im in tf_bold_data:
            ent = im.entities
            try:
                run = ent['run']
            except KeyError:
                run = "NA"
            print(f"{ent['subject']},{ent['session']},{ent['task']},{run},{ent['direction']},{ent['suffix']},{im.relpath},"
                  f"{fmaps_assigned},Multiple runs but some missing run numbers")
        continue

    fmap_sidecar_bids = layout.get(subject=subj, session=sess, run=3, datatype='fmap', extension='json')
    fmap_sidecar_paths = [file.path for file in fmap_sidecar_bids]
    tf_bold_intendedfor_paths = [file.relpath.replace(f'sub-{subj}/', '') for file in tf_bold_data]
    fmaps_assigned = intendFmaps(fmap_sidecar_paths, tf_bold_intendedfor_paths)
    for im in tf_bold_data:
        ent = im.entities
        # Still check for run- here because one task may have run- and the other not
        try:
            run = ent['run']
        except KeyError:
            run = "NA"
        print(f"{ent['subject']},{ent['session']},{ent['task']},{run},{ent['direction']},{ent['suffix']},{im.relpath},{fmaps_assigned},None")
