import flywheel
import os
import pandas as pd
import numpy as np
import argparse
import json
from datetime import date, datetime

expectedNumDicomFiles = {
    'dMRI_dir98_AP': 99,
    'dMRI_dir98_AP_SBRef': 1,
    'dMRI_dir98_PA': 99,
    'dMRI_dir98_PA_SBRef': 1,
    'dMRI_dir99_AP': 100,
    'dMRI_dir99_AP_SBRef': 1,
    'dMRI_dir99_PA': 100,
    'dMRI_dir99_PA_SBRef': 1,
    'rfMRI_REST_AP': 420,
    'rfMRI_REST_AP_SBRef': 1,
    'rfMRI_REST_PA': 420,
    'rfMRI_REST_PA_SBRef': 1,
    'SpinEchoFieldMap_AP': 3,
    'SpinEchoFieldMap_PA': 3,
    'SPIRAL_V20_HCP_ASL': 986,
    'SPIRAL_V20_HCP_M0': 68,
    'SPIRAL_V20_HCP_MeanPerf': 34,
    'T1w_MPR': 208,
    'T2w_SPC': 208,
    'tfMRI_GAMBLING_AP': 228,
    'tfMRI_GAMBLING_AP_SBRef': 1,
    'tfMRI_GAMBLING_PA': 228,
    'tfMRI_GAMBLING_PA_SBRef': 1,
    'tfMRI_WM_AP': 365,
    'tfMRI_WM_AP_SBRef': 1,
    'tfMRI_WM_PA': 365,
    'tfMRI_WM_PA_SBRef': 1
    }

fw = flywheel.Client()
project = fw.lookup('pennftdcenter/HCPMultiCenter')

all_info = dict()

for sub in project.subjects():
    sub_id = sub.id
    sub_label = sub.label
    for ses in sub.sessions():
        ses_id = ses.id
        ses_label = ses.label
        for acq in ses.acquisitions():
            acq = acq.reload()
            acq_id = acq.id
            acq_label = acq.label
            acq_series_description = 'NA'
            acq_series_number = 'NA'
            acq_study_date = 'NA'
            acq_found_dicom = False
            acq_num_dicom_files = 0
            acq_missing_info = False
            acq_complete = False
            for f in acq.files:
                if f.type != 'dicom':
                    next
                acq_found_dicom = True
                file_info = f.info
                if (not file_info):
                    acq_missing_info = True

                extension = os.path.splitext(f.name)[1]
                acq_num_dicom_files = 1
                if (extension == '.zip'):
                    acq_num_dicom_files = f.zip_member_count
                try:
                    acq_series_description = file_info['SeriesDescription']
                except KeyError:
                    acq_series_description = 'NA'
                try:
                    acq_series_number = file_info['SeriesNumber']
                except KeyError:
                    acq_series_number = 'NA'
                try:
                    acq_study_date = file_info['StudyDate']
                except KeyError:
                    print('No study date for acquisition {}/{}/{} {}'.format(sub.label, ses.label, acq_label, acq.id))
                    acq_study_date = 'NA'
                break
            acq_ignore = (acq_series_description != 'NA' and not (acq_series_description in expectedNumDicomFiles.keys()))
            if (acq_series_description != 'NA' and (acq_series_description in expectedNumDicomFiles.keys())):
                acq_complete = (acq_num_dicom_files == expectedNumDicomFiles[acq_series_description])
            all_info[acq_id] = [sub_id, sub_label, ses_id, ses_label, acq_label, acq_study_date, acq_series_number, acq_series_description,
                                acq_missing_info, acq_ignore, acq_found_dicom, acq_num_dicom_files, acq_complete]


with open('HCPMultiCenterCompleteness.txt','w') as data:
    data.write(str(all_info))

with open('HCPMultiCenterCompleteness.json', 'w') as convert_file:
    convert_file.write(json.dumps(all_info))

df = pd.DataFrame.from_dict(all_info, orient='index').reset_index()
df.columns=['AcquisitionID', 'SubjectID', 'SubjectLabel', 'SessionID', 'SessionLabel', 'AcquisitionLabel', 'StudyDate', 'SeriesNumber', 'SeriesDescription',
                            'MissingInfo', 'Ignore', 'FoundDicom', 'NumDicomFiles','Complete']

# Export dataframe to csv
filename = f'HCPMultiCenterCompleteness.csv'
df.to_csv(filename,index=False)
