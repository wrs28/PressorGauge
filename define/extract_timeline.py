import pandas as pd
import os
import re
import datetime as dt
from typing import List
from sqlalchemy import create_engine

from definitions import mimic_dir, tables
import vent_filters


ce = pd.DataFrame({
    "ICUSTAY_ID" : pd.Series([], dtype=pd.Int64Dtype()),
    "CHARTTIME"  : pd.Series([], dtype=str),
    "MV_BOOL"    : pd.Series([], dtype=bool),
    "OX_BOOL"    : pd.Series([], dtype=bool),
    "EX_BOOL"    : pd.Series([], dtype=bool),
    "SE_BOOL"    : pd.Series([], dtype=bool),
})

columns = list(ce.columns)

path = os.path.join(mimic_dir, tables["procedureevents_mv"] + ".csv")
pmv = pd.read_csv(path, dtype= {"VALUE" : float}, parse_dates = ["STARTTIME","ENDTIME","STORETIME"]) #, "ERROR" : int, "RESULTSTATUS" : str}):
pmv["MV_BOOL"] = False
pmv["OX_BOOL"] = False
pmv["EX_BOOL"] = pmv.apply(vent_filters.metavision_extubation, axis=1)
pmv["SE_BOOL"] = (pmv["ITEMID"] == 225468)
pmv.rename(columns={"STARTTIME" : "CHARTTIME"}, inplace=True)

ce = ce.append(pmv.loc[(pmv["EX_BOOL"] | pmv["SE_BOOL"]), columns])

count = 0
path = os.path.join(mimic_dir, tables["chartevents"] + ".csv")
for chunk in pd.read_csv(path, chunksize=1*(10**4), dtype= {"VALUE" : str}, parse_dates = ["CHARTTIME"]): #, "ERROR" : int, "RESULTSTATUS" : str}):
    count += 1
    chunk["MV_BOOL"] = chunk.apply(vent_filters.mechanical_vent, axis=1)
    chunk["OX_BOOL"] = chunk.apply(vent_filters.oxygen_therapy, axis=1)
    chunk["EX_BOOL"] = chunk.apply(vent_filters.extubation, axis=1)
    chunk["SE_BOOL"] = chunk.apply(vent_filters.self_extubation, axis=1)
    ce = ce.append(chunk.loc[chunk.apply(vent_filters.relevant, axis=1), columns])
    if count > 1:
        break

ce.sort_values(by="CHARTTIME", inplace=True)

vent_times = pd.DataFrame({
    "ICUSTAY_ID" : pd.Series([], dtype=pd.Int64Dtype()),
    "CHARTTIME" : pd.Series([], dtype=str),
    "ISVENTED" : pd.Series([], dtype=bool),
    "VENTEPISODE" : pd.Series([], dtype=bool),#pd.Int16Dtype()),
})

for name, group in ce.groupby(["ICUSTAY_ID","CHARTTIME"]):
    temp =  pd.DataFrame({
        "ICUSTAY_ID" : [name[0]],
        "CHARTTIME" : name[1],
        "ISVENTED" : group["MV_BOOL"].any() & ~group["OX_BOOL"].any() & ~group["EX_BOOL"].any() & ~group["SE_BOOL"].any() ,
    })
    vent_times = vent_times.append(temp)

print(vent_times)

# for name, group in vent_times.groupby("ICUSTAY_ID"):
#     vent_times.loc[vent_times["ICUSTAY_ID"]==name, "subgroup"] = (group["vented"] != group["vented"].shift(1)).cumsum()
#
# engine = create_engine('postgres://wrs:wrs@localhost/insight_project')
# vent_times.to_sql("vents", engine)
