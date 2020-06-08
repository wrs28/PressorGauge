import pandas as pd
import os
import math
import numpy as np
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables


# number of rows in CHARTEVENTS to read in at a time (there are 330_712_483 lines in CHARTEVENTS)
CHUNK_SIZE = 10**6
NUM_CHUNKS = np.inf


# time window from end of intubation episode that chart data is extracted
WINDOW_SIZE = pd.Timedelta(hours=6)


# load in ventilation times
path = os.path.join(processed_data_dir, "vaso_episodes.h5")
vaso_episodes = pd.read_hdf(path, "vaso_episodes")

path = os.path.join(mimic_dir, tables["icustays"] + ".csv")
icu = pd.read_csv(path, usecols=["ICUSTAY_ID","SUBJECT_ID"])
vaso_episodes = vaso_episodes.join(icu.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")


# initialize chartevents dataframe
ce_columns = ["SUBJECT_ID", "ITEMID", "CHARTTIME", "VALUE", "VALUENUM", "VALUEUOM","FLAG"]
dtypes = {
  "VALUE" : str,
  "VALUENUM" : float,
  "VALUEUOM" : str,
  "FLAG" : str,
}


print("Extracting relevent lab events")
path = os.path.join(mimic_dir, tables["labevents"] + ".csv")
ce_lists = [[] for i in range(12)]
# window_times = [[] for i in range(12)]
count = 0
for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=ce_columns, dtype=dtypes, parse_dates = ["CHARTTIME"]):
  count += 1
  if count <= NUM_CHUNKS:
    print("\tprocessing LABEVENTS chunk:",count, "of", math.ceil(27_854_055/CHUNK_SIZE))
    for (subject, episode), group in vaso_episodes.groupby(["SUBJECT_ID", "EPISODE"]):
      # only extract chart data from before end of first intubation episode
      if episode==1:
        # one window period before end of episode
        for time, time_group in chunk[chunk.SUBJECT_ID == subject].groupby("CHARTTIME"):
          time_group = time_group.copy()
          # one window period before end of episode
          for i in range(len(ce_lists)):
            interval = pd.Interval(group.STARTTIME.iloc[0] - (i+1)*WINDOW_SIZE, group.STARTTIME.iloc[0] - i*WINDOW_SIZE, closed="both")
            # but only keep those in the window
            if time in interval:
              time_group["WINDOW_MID"] = interval.mid
              ce_lists[i].append(time_group)
  else:
    break


for i in range(len(ce_lists)):
  ce = ce_lists[i]
  if len(ce) > 0:
    ce_lists[i] = pd.concat(ce)
  else:
    ce_lists[i] = pd.DataFrame(columns=ce_lists[0].columns.to_list())


# save out result
def ce_to_int(ce):
  ce.SUBJECT_ID = ce.SUBJECT_ID.astype(int)
  ce.ITEMID = ce.ITEMID.astype(int)
  return None


print("Saving processed chart events")
path = os.path.join(processed_data_dir, "lab_data.h5")
for i in range(len(ce_lists)):
  ce = ce_lists[i]
  ce_to_int(ce)
  if i==0:
    mode="w"
  else:
    mode="a"
  ce.to_hdf(path, "labs" + str(i), mode=mode, format="Table")


print("Done processing lab events!")
print()
