import pandas as pd
# pd.set_option("display.max_rows", None, "display.max_columns", None)
import math
import numpy as np
import os
import re
import datetime as dt
from sqlalchemy import create_engine

from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables, ventids, oxygenvals
import vent_filters


ce = pd.read_hdf(os.path.join(processed_data_dir, "chart_flagged_by_vent.h5"), "vents")


nrows = len(ce)
ce.sort_values(by="CHARTTIME", inplace=True)


# build vent_times, determined by being on mech vent and not being any of oxy therapy, or extubated
print("Processing ventilation status in chart record")
count = 0
row_pointer = 0
dict_list = []
for name, group in ce.groupby(["ICUSTAY_ID","CHARTTIME"]):
  dict_list.append({
    "ICUSTAY_ID" : name[0],
    "CHARTTIME" : name[1],
    "ISVENTED" : group["MV_BOOL"].any() & ~group["OX_BOOL"].any() & ~group["EX_BOOL"].any() & ~group["SE_BOOL"].any() ,
  })
  row_pointer += len(group)
  if count % 10000 == 0:
    print("\tprocessed", row_pointer, "rows of", nrows)
  count += 1
vent_times = pd.DataFrame.from_dict(dict_list)


# find first true element in boolean array
def find_first(arr):
  return arr.argmax()


# find last true element in boolean array
def find_last(arr):
  return len(arr) - (find_first(arr[::-1]) + 1)


print("Processing start and stop ventilation times")
path = os.path.join(project_dir, "log.txt") # for logging ICUSTAY_IDs with just one time
dict_list = []
print_counter = 0
row_pointer = 0
nrows = len(vent_times)
with open(path, "w") as file:
  for icustay, group in vent_times.groupby("ICUSTAY_ID"):
    group = group.sort_values(by="CHARTTIME")
    episodes_by_time = (group.ISVENTED.shift(1) == False).cumsum() # flag beginning/end of ventilation episode
    episodes = episodes_by_time.dropna().unique()
    count = 0
    for episode in episodes:
      episode_indices = np.logical_and(episodes_by_time == episode, group.ISVENTED.values[0]) # subselect a particular episode
      is_vented_episode_start = find_first(episode_indices)#episode_indices.argmax() # find first episode
      is_vented_episode_stop = find_last(episode_indices)#len(episode_indices) - (episode_indices[::-1].argmax() + 1)
      if group.ISVENTED.values[is_vented_episode_start]: # only count if first time in episode includes mech vent
        count += 1
        starttime = group.iloc[is_vented_episode_start,1]
        stoptime = group.iloc[is_vented_episode_stop,1]
        # interval = pd.Interval(group.iloc[is_vented_episode_start,1], group.iloc[is_vented_episode_stop,1], closed="both")
        # if interval.left != interval.right: # record mech vent interval and episode number

        if starttime != stoptime:
          dict_list.append({
            "ICUSTAY_ID" : int(icustay),
            "STARTTIME" : starttime,
            "STOPTIME" : stoptime,
            "EPISODE" : int(count),
          })
        else: # throw away margin cases where there is only one mech vent data point
          print("singular mech vent event found in ICUSTAY_ID:", int(icustay), file=file)

    row_pointer += len(group)
    if print_counter % 10000 == 0:
      print("\tprocessed", row_pointer, "rows of", nrows)
    print_counter += 1

vent_episodes = pd.DataFrame.from_dict(dict_list)


# determine number of episodes for each ICUSTAY
print("Determining episodes from chart record.")
number_of_episodes = vent_episodes[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
vent_episodes = vent_episodes.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")


# drop rows for patients who die and have only one ventilation episode
print("Drop patients who expire after first extubation.")
path = os.path.join(mimic_dir, tables["icustays"] + ".csv")
icu = pd.read_csv(path, usecols=["ICUSTAY_ID","HADM_ID"]) # load icustays and hoptical admissions
path = os.path.join(mimic_dir, tables["admissions"] + ".csv")
adm = pd.read_csv(path, usecols=["DEATHTIME","HADM_ID"]) # load hospital admissions and deathtimes
admicu = adm.join(icu.set_index("HADM_ID"), on="HADM_ID", how="left") # join on hospital admissions
admicu = vent_episodes.join(admicu.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left") # expand admicu to size of vent_episodes, joined on ICUSTAY_IDs
vent_episodes = vent_episodes[ (pd.isna(admicu["DEATHTIME"]) & vent_episodes["NUMBER_OF_EPISODES"]==1) | (vent_episodes["NUMBER_OF_EPISODES"]>1) ] # remove rows where patient dies after first extubation

# engine = create_engine('postgres://wrs:wrs@localhost/insight_project')
print("Saving ventilation episodes.")
path = os.path.join(processed_data_dir, "ventilation_times.h5")
vent_episodes.to_hdf(path, "vents", mode="w", format="table")

print("Done processing ventilation times!")
