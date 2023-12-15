import flywheel

fw = flywheel.Client()

## YOUR PROJECT HERE
project = fw.lookup("")

sessions = project.sessions()

class_gear = fw.lookup('gears/dicom-mr-classifier')

for sess in sessions:

    acquisitions = sess.acquisitions()

    for acq in acquisitions:
        # If acq label contains 'dMRI_', then check if the classification is empty
        # If it is empty, the classification on the site will be "MR". If it is correct,
        # classification will be "MR: " followed by a comma-separated list of values in the
        # f.classification dict
        if (acq.label.find('dMRI_') != -1):
            for f in acq.files:
                if f.type == 'dicom' and len(f.classification) == 0:
                    print(f"Re-running classification for {sess.label}/{acq.label}/{f.name}")
                    class_gear.run(inputs={'dicom': f})
