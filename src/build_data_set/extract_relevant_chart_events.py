import pandas as pd

import numpy as np
import os
import re
import datetime as dt
from sqlalchemy import create_engine

from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables
import vent_filters


# number of rows in CHARTEVENTS to read in at a time (there are 330_712_483 lines in CHARTEVENTS)
CHUNK_SIZE = 10**5


# time window from end of intubation episode that chart data is extracted
WINDOW_SIZE = pd.Timedelta(hours=1)


# load in ventilation times
path = os.path.join(processed_data_dir, "ventilation_times.h5")
vent_episodes = pd.read_hdf(path, "vents")


# initialize chartevents dataframe
ce = pd.DataFrame({
  "SUBJECT_ID" : pd.Series([], dtype=pd.Int32Dtype()),
  "ICUSTAY_ID" : pd.Series([], dtype=pd.Int32Dtype()),
  "ITEMID"     : pd.Series([], dtype=pd.Int32Dtype()),
  "CHARTTIME"  : pd.Series([], dtype=str),
  "VALUE"      : pd.Series([], dtype=str),
  "VALUENUM"   : pd.Series([], dtype=float),
  "VALUEUOM"   : pd.Series([], dtype=str),
})


count = 0
path = os.path.join(mimic_dir, tables["chartevents"] + ".csv")
for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=list(ce.columns), dtype= {"VALUE" : str}, parse_dates = ["CHARTTIME"]):
  count += 1
  for name, group in vent_episodes.groupby(["ICUSTAY_ID", "EPISODE"]):
    if name[1]==1: # only extract chart data from before end of first intubation episode
      interval = pd.Interval(group.PERIOD.values[0].right - WINDOW_SIZE, group.PERIOD.values[0].right) # one window period before end of episode
      for time, time_group in chunk[chunk["ICUSTAY_ID"] == name[0]].groupby("CHARTTIME"): # loop through all the times in a given ICUSTAY
        if time in interval: # but only keep those in the window
          ce = ce.append(time_group)
  if count > 1:
    break


# save out result
path = os.path.join(processed_data_dir, "chart_data.h5")
ce.to_hdf(path, "charts")
