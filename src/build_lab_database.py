import numpy as np

# number of rows in CHARTEVENTS to read in at a time (there are 330_712_483 lines in CHARTEVENTS)
CHUNK_SIZE = 10**6
NUM_CHUNKS = np.inf

import pandas as pd
import os
import math
import sqlalchemy
import progressbar
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables

# load in ventilation times
engine = sqlalchemy.create_engine('postgres://postgres:postgres@localhost/PressorGauge')
with engine.connect() as connection:
  vaso_episodes = pd.read_sql("pressors_by_icustay", con=connection, index_col="ICUSTAY_ID")

# initialize chartevents dataframe
columns = [
  "SUBJECT_ID",
  "ITEMID",
  "CHARTTIME",
  "VALUENUM",
  "FLAG",
  "HADM_ID"
]

dtypes = {
  "VALUENUM" : float,
  "FLAG" : str,
  "SUBJECT_ID" : pd.Int32Dtype(),
  "HADM_ID" : pd.Int32Dtype()
}

def find_first(arr):
  idx = arr.argmax()
  if arr[idx]:
    return idx
  else:
    return None#len(arr) - 1

with engine.connect() as connection:
  interval_splits = pd.read_sql("interval_splits", con=connection, index_col="ICUSTAY_ID")
interval_splits.set_index("HADM_ID", inplace=True)


print("extracting relevent lab events")
path = os.path.join(mimic_dir, tables["labevents"] + ".csv")
count = 0
replace_flag = True
with engine.connect() as connection:
  for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=columns, dtype=dtypes, parse_dates = ["CHARTTIME"]):
    # add columns to keep track of whether or not 24 hours from pressor (PRESSOR_LABEL)
    # and which hour before pressor event it it (HOURS_BEFORE_PRESSOR)
    chunk = chunk[~pd.isna(chunk.HADM_ID)]
    chunk["PRESSOR_LABEL"] = False
    chunk["HOURS_BEFORE_PRESSOR"] = 0
    temp = chunk.join(vaso_episodes[["HADM_ID","INTIME"]].set_index("HADM_ID"),on="HADM_ID")
    chunk.CHARTTIME = np.int32((chunk.CHARTTIME - temp.INTIME).values/10**9)
    count += 1
    if count <= NUM_CHUNKS:
      print("\tprocessing LABEVENTS chunk:",count, "of", math.ceil(27_854_055/CHUNK_SIZE))
      # loop through all the times in a given ICUSTAY
      for (time, hadm), time_group in chunk[chunk.HADM_ID.isin(vaso_episodes.HADM_ID)].groupby(["CHARTTIME","HADM_ID"]):
        # only extract chart data from 2 days before pressor event
        splits = interval_splits.loc[hadm]
        i = find_first((splits[1:-1].values < time) & (time <= splits[:-2].values))
        if i:
          time_group = time_group.copy()
          time_group.HOURS_BEFORE_PRESSOR = i
          # if within one day of pressor event, lable true if episode==1
          if i < 24:
            time_group.PRESSOR_LABEL = vaso_episodes[vaso_episodes.HADM_ID==hadm].EPISODE.iloc[0]==1
          # if first entry to be added, replace table, otherwise add to it
          if replace_flag:
            mode = "replace"
            replace_flag = False
          else:
            mode = "append"
          time_group.to_sql("lab_events", con=connection, if_exists=mode, index=False)
    else:
      break


print("Done processing lab events!")
print()
