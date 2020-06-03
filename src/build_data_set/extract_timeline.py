import pandas as pd
import numpy as np
import os
import re
import datetime as dt
from sqlalchemy import create_engine

# pd.set_option("display.max_rows", None, "display.max_columns", None)
CHUNK_SIZE = 10**6 # number of rows in CHARTEVENTS to read in at a time (there are 330_712_483 lines in CHARTEVENTS)

from definitions import project_dir, mimic_dir, tables, ventids, oxygenvals
import vent_filters


# initialize chartevents dataframe
ce = pd.DataFrame({
    "ICUSTAY_ID" : pd.Series([], dtype=pd.Int32Dtype()),
    "CHARTTIME"  : pd.Series([], dtype=str),
    "MV_BOOL"    : pd.Series([], dtype=bool),
    "OX_BOOL"    : pd.Series([], dtype=bool),
    "EX_BOOL"    : pd.Series([], dtype=bool),
    "SE_BOOL"    : pd.Series([], dtype=bool),
})


# load procedureevents_mv for extubation events
path = os.path.join(mimic_dir, tables["procedureevents_mv"] + ".csv")
pmv = pd.read_csv(path, dtype= {"VALUE" : float}, parse_dates = ["STARTTIME","ENDTIME","STORETIME"]) #, "ERROR" : int, "RESULTSTATUS" : str}):
pmv["MV_BOOL"] = False
pmv["OX_BOOL"] = False
pmv["EX_BOOL"] = pmv.apply(vent_filters.metavision_extubation, axis=1)
pmv["SE_BOOL"] = (pmv["ITEMID"] == 225468)
pmv.rename(columns={"STARTTIME" : "CHARTTIME"}, inplace=True)


# add extubation events to chartevents
ce = ce.append(pmv.loc[(pmv["EX_BOOL"] | pmv["SE_BOOL"]), list(ce.columns)])


# read in chartevents by chunk (it's too big otherwise), tagging by mech vent, oxy therapy, or extubation status
count = 0
path = os.path.join(mimic_dir, tables["chartevents"] + ".csv")
for chunk in pd.read_csv(path, chunksize=2*(10**4), usecols=["ITEMID","VALUE","ICUSTAY_ID","CHARTTIME"], dtype= {"VALUE" : str}, parse_dates = ["CHARTTIME"]):
    # print(chunk[chunk.ICUSTAY_ID == 247247])
    count += 1
    chunk["MV_BOOL"] = chunk.apply(vent_filters.mechanical_vent, axis=1)
    chunk["OX_BOOL"] = chunk.apply(vent_filters.oxygen_therapy, axis=1)
    chunk["EX_BOOL"] = chunk.apply(vent_filters.extubation, axis=1)
    chunk["SE_BOOL"] = chunk.apply(vent_filters.self_extubation, axis=1)
    ce = ce.append(chunk.loc[chunk.apply(vent_filters.isrelevant, axis=1), list(ce.columns)])
    if count > 1:
        break


ce.sort_values(by="CHARTTIME", inplace=True)


# initialize ventilation times auxilliary dataframe
vent_times = pd.DataFrame({
    "ICUSTAY_ID" : pd.Series([], dtype=pd.Int32Dtype()),
    "CHARTTIME" : pd.Series([], dtype=str),
    "ISVENTED" : pd.Series([], dtype=bool),
})


# build vent_times by being on mech vent and not being any of oxy therapy, or extubated
for name, group in ce.groupby(["ICUSTAY_ID","CHARTTIME"]):
    vent_times = vent_times.append(pd.DataFrame({
        "ICUSTAY_ID" : [name[0]],
        "CHARTTIME" : [name[1]],
        "ISVENTED" : group["MV_BOOL"].any() & ~group["OX_BOOL"].any() & ~group["EX_BOOL"].any() & ~group["SE_BOOL"].any() ,
    }))


# initialize vent_episodes
vent_episodes = pd.DataFrame({
    "ICUSTAY_ID" : pd.Series([], dtype=pd.Int32Dtype()),
    "PERIOD" : pd.Series([], dtype=str),
    "EPISODE" : pd.Series([], dtype=pd.Int16Dtype()),
})

path = os.path.join(project_dir, "log.txt")
with open(path, "w") as file:
    for icustay, group in vent_times.groupby("ICUSTAY_ID"):
        # if icustay == 247247:
        group = group.sort_values(by="CHARTTIME")
        # flag beginning/end of ventilation episode
        episodes_by_time = (group.ISVENTED.shift(1) == False).cumsum()
        episodes = episodes_by_time.dropna().unique()
        count = 0
        for episode in episodes:
            episode_indices = np.logical_and(episodes_by_time == episode, group.ISVENTED.values[0])
            is_vented_episode_start = episode_indices.argmax()
            is_vented_episode_stop = len(episode_indices) - (episode_indices[::-1].argmax() + 1)
            if group.ISVENTED.values[is_vented_episode_start]:
                count += 1
                interval = pd.Interval(group.iloc[is_vented_episode_start,1], group.iloc[is_vented_episode_stop,1], closed="both")
                # record mech vent interval and episode number
                if interval.left != interval.right:
                    vent_episodes = vent_episodes.append(pd.DataFrame({
                        "ICUSTAY_ID" : [icustay],
                        "PERIOD" : [interval],
                        "EPISODE" : [count],
                    }))
                # throw away margin cases where there is only one mech vent data point
                else:
                    print("Singular mech vent event found in ICUSTAY_ID:", int(icustay), file=file)


# drop rows for patients who die and have only one ventilation episode
path = os.path.join(mimic_dir, tables["icustays"] + ".csv")
icu = pd.read_csv(path, usecols=["ICUSTAY_ID","HADM_ID"])
path = os.path.join(mimic_dir, tables["admissions"] + ".csv")
adm = pd.read_csv(path, usecols=["DEATHTIME","HADM_ID"])
admicu = adm.join(icu.set_index("HADM_ID"), on="HADM_ID", how="left")
number_of_episodes = vent_episodes[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
admicu = admicu.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
admicu = vent_episodes.join(admicu.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")

vent_episodes = vent_episodes.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
vent_episodes = vent_episodes[ (pd.isna(admicu["DEATHTIME"]) & vent_episodes["NUMBER_OF_EPISODES"]==1) | (vent_episodes["NUMBER_OF_EPISODES"]>1) ]

# engine = create_engine('postgres://wrs:wrs@localhost/insight_project')
path = os.path.join(project_dir, "ventilation_times.h5")
vent_episodes.to_hdf(path, "vents")
