import pandas as pd
import os
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables

dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "ventnum" : pd.Int16Dtype(),
  "duration_hours" : float,
}

path = os.path.join(mimic_dir, "ventdurations.csv")
vent_episodes = pd.read_csv(path, dtype=dtypes,  parse_dates = ["starttime", "endtime"])
vent_episodes.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "ventnum"        : "EPISODE",
    "starttime"      : "STARTTIME",
    "endtime"        : "ENDTIME",
    "duration_hours" : "DURATION_HOURS"
})


vent_episodes.dropna(axis=0,inplace=True) # 34 na icustays
number_of_episodes = vent_episodes[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
vent_episodes = vent_episodes.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")


# drop rows for patients who die and have only one ventilation episode
path = os.path.join(mimic_dir, tables["icustays"] + ".csv")
icu = pd.read_csv(path, usecols=["ICUSTAY_ID","HADM_ID"], dtype={"ICUSTAY_ID" : pd.Int32Dtype()}) # load icustays and hoptical admissions
path = os.path.join(mimic_dir, tables["admissions"] + ".csv")
adm = pd.read_csv(path, usecols=["HOSPITAL_EXPIRE_FLAG","HADM_ID"], dtype={"HADM_ID" : pd.Int32Dtype(), "HOSPITAL_EXPIRE_FLAG" : bool}) # load hospital admissions and deathtimes
admicu = adm.join(icu.set_index("HADM_ID"), on="HADM_ID", how="left") # join on hospital admissions
admicu = vent_episodes.join(admicu.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left") # expand admicu to size of vent_episodes, joined on ICUSTAY_IDs
vent_episodes = vent_episodes[ ~(admicu.HOSPITAL_EXPIRE_FLAG & vent_episodes.NUMBER_OF_EPISODES==1) ] # remove rows where patient dies after first extubation

# remove episodes with more than 24 hours between
ve_list = []
for (icustay, numeps), group in vent_episodes.groupby(["ICUSTAY_ID","NUMBER_OF_EPISODES"]):
  if numeps > 1:
    if (group.iloc[1,2] - group.iloc[0,3]) < pd.Timedelta(days=1):
      ve_list.append(group)
  else:
    ve_list.append(group)
vent_episodes = pd.concat(ve_list)

vent_episodes = vent_episodes[ (vent_episodes.EPISODE==1) ]

vent_episodes.ICUSTAY_ID = vent_episodes.ICUSTAY_ID.astype(int)
vent_episodes.EPISODE = vent_episodes.EPISODE.astype(int)

path = os.path.join(processed_data_dir, "vent_episodes.h5")
vent_episodes.to_hdf(path, "vent_episodes", format="table", mode="w")
