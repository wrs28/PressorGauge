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


# number of rows in CHARTEVENTS to read in at a time (there are 330_712_483 lines in CHARTEVENTS)
CHUNK_SIZE = 10**4
NUM_CHUNKS = 5#np.inf


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
print("Reading PROCEDUREEVENTS_MV.csv")
path = os.path.join(mimic_dir, tables["procedureevents_mv"] + ".csv")
pmv = pd.read_csv(path, dtype= {"VALUE" : float, "ICUSTAY_ID" : pd.Int32Dtype()}, parse_dates = ["STARTTIME","ENDTIME","STORETIME"]) #, "ERROR" : int, "RESULTSTATUS" : str}):
pmv["MV_BOOL"] = False
pmv["OX_BOOL"] = False
pmv["EX_BOOL"] = pmv.apply(vent_filters.metavision_extubation, axis=1)
pmv["SE_BOOL"] = (pmv["ITEMID"] == 225468)
pmv.rename(columns={"STARTTIME" : "CHARTTIME"}, inplace=True)


# add extubation events to chartevents
ce = ce.append(pmv.loc[(pmv["EX_BOOL"] | pmv["SE_BOOL"]), list(ce.columns)])


# read in chartevents by chunk (it's too big otherwise), tagging by mech vent, oxy therapy, or extubation status
print("Reading CHARTEVENTS.csv")
count = 0
path = os.path.join(mimic_dir, tables["chartevents"] + ".csv")
for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=["ITEMID","VALUE","ICUSTAY_ID","CHARTTIME"], dtype= {"VALUE" : str}, parse_dates = ["CHARTTIME"]):
  # print(chunk[chunk.ICUSTAY_ID == 247247])
  count += 1
  print("\treading CHARTEVENTS chunk:",count, "of", math.ceil(330712483/CHUNK_SIZE))
  chunk["MV_BOOL"] = chunk.apply(vent_filters.mechanical_vent, axis=1)
  chunk["OX_BOOL"] = chunk.apply(vent_filters.oxygen_therapy, axis=1)
  chunk["EX_BOOL"] = chunk.apply(vent_filters.extubation, axis=1)
  chunk["SE_BOOL"] = chunk.apply(vent_filters.self_extubation, axis=1)
  ce = ce.append(chunk.loc[chunk.apply(vent_filters.isrelevant, axis=1), list(ce.columns)])
  ce.to_hdf(os.path.join(processed_data_dir, "chart_flagged_by_vent.h5"), "vents", mode="w")
  if count > NUM_CHUNKS:
    break


ce.to_hdf(os.path.join(processed_data_dir, "chart_flagged_by_vent.h5"), "vents", mode="w")

print("Done flagging ventilation times!")
