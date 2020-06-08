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


# initialize chartevents dataframe
ce_columns = ["SUBJECT_ID", "ICUSTAY_ID", "ITEMID", "CHARTTIME", "VALUE", "VALUENUM", "VALUEUOM"]
dtypes = {
  "VALUE" : str,
  "VALUENUM" : float,
  "VALUEUOM" : str
}


print("Extracting relevent chart events")
path = os.path.join(mimic_dir, tables["chartevents"] + ".csv")
ce_lists = [[] for i in range(12)]
count = 0
for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=ce_columns, dtype=dtypes, parse_dates = ["CHARTTIME"]):
  count += 1
  if count <= NUM_CHUNKS:
    print("\tprocessing CHARTEVENTS chunk:",count, "of", math.ceil(330_712_483/CHUNK_SIZE))
    for (icustay, episode), group in vaso_episodes.groupby(["ICUSTAY_ID", "EPISODE"]):
      # only extract chart data from before end of first intubation episode
      if episode==1:
        # loop through all the times in a given ICUSTAY
        for time, time_group in chunk[chunk.ICUSTAY_ID == icustay].groupby("CHARTTIME"):
          time_group = time_group.copy()
          # one window period before end of episode
          for i in range(len(ce_lists)):
            interval = pd.Interval(group.STARTTIME.iloc[0] - (i+1)*WINDOW_SIZE, group.STARTTIME.iloc[0] - i*WINDOW_SIZE, closed="both")
            # but only keep those in the window
            if time in interval:
              time_group["WINDOW_MID"] = interval.mid
              ce_lists[i].append(time_group)
              # ce_lists[i]["WINDOW_MID"] = interval.mid
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
  ce.ICUSTAY_ID = ce.ICUSTAY_ID.astype(int)
  ce.SUBJECT_ID = ce.SUBJECT_ID.astype(int)
  ce.ITEMID = ce.ITEMID.astype(int)
  return None


print("Saving processed chart events")
path = os.path.join(processed_data_dir, "chart_data.h5")
for i in range(len(ce_lists)):
  ce = ce_lists[i]
  ce_to_int(ce)
  if i==0:
    mode="w"
  else:
    mode="a"
  ce.to_hdf(path, "charts" + str(i), mode=mode, format="Table")

print("Done processing chart events!")
print()
