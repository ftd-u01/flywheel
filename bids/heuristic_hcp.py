import datetime
import numpy as np
import os

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

# anatomical images
t1wn = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_rec-norm_T1w')
t2wn = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_rec-norm_T2w')


# field maps
fm_ap_task = create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-AP_epi')
fm_pa_task = create_key(
    'sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-PA_epi')

# functional scans
nback_ap = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-WM_dir-AP_bold')
nback_pa = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-WM_dir-PA_bold')
gamb_ap = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-gambling_dir-AP_bold')
gamb_pa = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-gambling_dir-PA_bold')
rest_ap = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_dir-AP_bold')
rest_pa = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_dir-PA_bold')

rest_ap_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_dir-AP_sbref')
rest_pa_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_dir-PA_sbref')

#ASL
asl = create_key('sub-{subject}/{session}/perf/sub-{subject}_{session}_task-rest_asl')
asl_mz = create_key('sub-{subject}/{session}/perf/sub-{subject}_{session}_task-rest_m0scan')
asl_mp = create_key('sub-{subject}/{session}/perf/sub-{subject}_{session}_task-rest_deltam')

#Diffusion scans
dti_98dir_ap = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-98dir_dir-AP_dwi')
dti_98dir_pa = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-98dir_dir-PA_dwi')
dti_99dir_ap = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-99dir_dir-AP_dwi')
dti_99dir_pa = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-99dir_dir-PA_dwi')

#sbref images
wm_ap_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-WM_dir-AP_sbref')
wm_pa_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-WM_dir-PA_sbref')
gamb_ap_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-gambling_dir-AP_sbref')
gamb_pa_sbref = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-gambling_dir-PA_sbref')

dti_98dir_ap_sbref = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-98dir_dir-AP_sbref')
dti_98dir_pa_sbref = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-98dir_dir-PA_sbref')
dti_99dir_ap_sbref = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-99dir_dir-AP_sbref')
dti_99dir_pa_sbref = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-99dir_dir-PA_sbref')


from collections import defaultdict
def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where
        allowed template fields - follow python string module:
        item: index within category
        subject: participant id
        seqitem: run number during scanning
        subindex: sub index within group"""

    info = {
        t1wn: [], t2wn: [], nback_ap: [], nback_pa: [],gamb_ap: [], gamb_pa: [], wm_ap_sbref:[],wm_pa_sbref: [], gamb_ap_sbref: [], gamb_pa_sbref: [], rest_ap: [], rest_pa: [], rest_ap_sbref: [], rest_pa_sbref: [], fm_ap_task: [], fm_pa_task:[], asl: [], asl_mz: [], asl_mp: [], dti_98dir_ap: [], dti_98dir_pa: [],dti_99dir_ap: [], dti_99dir_pa: [], dti_98dir_ap_sbref: [], dti_98dir_pa_sbref: [], dti_99dir_ap_sbref: [], dti_99dir_pa_sbref: []}

    for s in seqinfo:
        protocol = s.protocol_name.lower()
        if "tfMRI_WM_AP_SBRef" in s.series_description:
            info[wm_ap_sbref].append(s.series_id)
        elif "tfMRI_WM_PA_SBRef" in s.series_description:
            info[wm_pa_sbref].append(s.series_id)
        elif "tfMRI_GAMBLING_AP_SBRef" in s.series_description:
            info[gamb_ap_sbref].append(s.series_id)
        elif "tfMRI_GAMBLING_PA_SBRef" in s.series_description:
            info[gamb_pa_sbref].append(s.series_id)
        elif "gambling_ap" in protocol:
            info[gamb_ap].append(s.series_id)
        elif "gambling_pa" in protocol:
            info[gamb_pa].append(s.series_id)
        elif "wm_ap" in protocol:
            info[nback_ap].append(s.series_id)
        elif "wm_pa" in protocol:
            info[nback_pa].append(s.series_id)
        elif "spinechofieldmap_pa" in protocol:
            info[fm_pa_task].append(s.series_id)
        elif "spinechofieldmap_ap" in protocol:
           info[fm_ap_task].append(s.series_id)
        elif "spiral_v20_hcp" in protocol and "M0" in s.series_description:
           info[asl_mz].append(s.series_id)
        elif "spiral_v20_hcp" in protocol and "MeanPerf" in s.series_description:
           info[asl_mp].append(s.series_id)
        elif "spiral_v20_hcp" in protocol:
           info[asl].append(s.series_id)
        elif s.series_description.endswith("_M0"):
            info[asl_mz].append(s.series_id)
        elif s.series_description.endswith("_MeanPerf"):
            info[asl_mp].append(s.series_id)
        elif s.series_description.endswith("_ASL"):
            info[asl].append(s.series_id)
        elif "dMRI_dir98_AP_SBRef" in s.series_description:
            info[dti_98dir_ap_sbref].append(s.series_id)
        elif "dMRI_dir98_PA_SBRef" in s.series_description:
            info[dti_98dir_pa_sbref].append(s.series_id)
        elif "dMRI_dir99_AP_SBRef" in s.series_description:
            info[dti_99dir_ap_sbref].append(s.series_id)
        elif "dMRI_dir99_PA_SBRef" in s.series_description:
            info[dti_99dir_pa_sbref].append(s.series_id)
        elif "dmri_dir98_ap" in protocol:
            info[dti_98dir_ap].append(s.series_id)
        elif "dmri_dir98_pa" in protocol:
            info[dti_98dir_pa].append(s.series_id)
        elif "dmri_dir99_ap" in protocol:
            info[dti_99dir_ap].append(s.series_id)
        elif "dmri_dir99_pa" in protocol:
            info[dti_99dir_pa].append(s.series_id)
        elif "rfMRI_REST_AP_SBRef" in s.series_description:
            info[rest_ap_sbref].append(s.series_id)
        elif "rfMRI_REST_PA_SBRef" in s.series_description:
            info[rest_pa_sbref].append(s.series_id)
        elif "rfMRI_REST_AP" in s.series_description:
            info[rest_ap].append(s.series_id)
        elif "rfMRI_REST_PA" in s.series_description:
            info[rest_pa].append(s.series_id) 
        elif "t1w" in protocol and 'NORM' in s.image_type:
            info[t1wn].append(s.series_id)
        elif "t2w" in protocol and 'NORM' in s.image_type:
            info[t2wn].append(s.series_id)
        else:
            print("Series not recognized!: ", protocol, s.dcm_dir_name)

# Get timestamp info to use as a sort key.
    def get_date(series_info):
        return(datetime.datetime.strptime(series_info.date, '%Y-%m-%dT%H:%M:%S.%f'))


    # Before returning the info dictionary, 1) get rid of empty dict entries; and
    # 2) for entries that have more than one series, differentiate them by run-{index}.
    def update_key(series_key, runindex):
        series_name = series_key[0]
        s = series_name.split("_")
        nfields = len(s)
        s.insert(nfields-1, "run-" + str(runindex))
        new_name = "_".join(s)
        return((new_name, series_key[1], series_key[2]))

    newdict = {}
    delkeys = []
    for k in info.keys():
        ids = info[k]
        unique_ids = list(set(ids))
        if len(unique_ids) > 1:
            series_list = [s for s in seqinfo if (s.series_id in unique_ids)]
            unique_tuples = list(set([(s.series_uid, get_date(s)) for s in series_list]))
            # Sort the series UIDs by time of acquisition.
            def sortfunc(mytuple):
                return(mytuple[1])
            unique_tuples.sort(key = sortfunc)
            uids = []
            for val in unique_tuples:
                if not val[0] in uids:
                    uids.append(val[0])
#            print("unique_tuples: ",unique_tuples)
            nseries = len(uids)
            newkeys = [update_key(k, i) for i in range(1, nseries + 1)]
#            print("newkeys: ", newkeys)
#            print("series_list: ", [(s.series_id, get_date(s)) for s in series_list])
            delkeys.append(k)
            for i in range(nseries):
                series_matches = [s for s in series_list if s.series_uid == uids[i]]
                newdict[newkeys[i]] = []
                for match in series_matches:
                    newdict[newkeys[i]].append(match.series_id)
    # Merge the two dictionaries.
    info.update(newdict)

    # Delete keys that were expanded on in the new dictionary.
    for k in delkeys:
        info.pop(k, None)

#    for k,v in info.items():
#        if len(info[k]) > 0:
#            for vals in v:
#                print(k,vals)

    return info

    def ReplaceSession(sesname):
        return sesname[:10].replace("-", '')
