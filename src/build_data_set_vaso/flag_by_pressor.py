import pandas as pd
import math
import numpy as np
import os

from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables, pressor_ids
import vaso_filters

# hdf file name that will store results
flagged_by_pressor_path = os.path.join(processed_data_dir, "flagged_by_pressor.h5")


# number of rows in INPUTEVENTS_MV to read in at a time (there are 3_618_991 lines in CHARTEVENTS)
CHUNK_SIZE = 10**6
NUM_CHUNKS = 5#np.inf


# initialize chartevents dataframe
ce = pd.DataFrame({
  "ICUSTAY_ID" : pd.Series([], dtype=pd.Int32Dtype()),
  "STARTTIME"  : pd.Series([], dtype=str),
  "PRESSOR"    : pd.Series([], dtype=bool),
})


# read in chartevents by chunk (it's too big otherwise), tagging by mech vent, oxy therapy, or extubation status
print("Reading INPUTEVENTS_MV.csv")
path = os.path.join(mimic_dir, tables["inputevents_mv"] + ".csv")
dtypes = {"ICUSTAY_ID": pd.Int32Dtype(), "ITEMID": pd.Int32Dtype()}
count = 0
for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=["ICUSTAY_ID","ITEMID","STARTTIME"], parse_dates = ["STARTTIME"], dtype=dtypes):
  count += 1
  if count <= NUM_CHUNKS:
    print("\treading INPUTEVENTS_MV chunk:",count, "of", math.ceil(3_618_991/CHUNK_SIZE))
    chunk["PRESSOR"] = chunk.apply(vaso_filters.pressor, axis=1) # on pressors?
    ce = ce.append(chunk.loc[chunk.PRESSOR, list(ce.columns)]) # then add icustay, itemid, and starttime
    # ce.ICUSTAY_ID = ce.ICUSTAY_ID.astype(int)
    # ce.to_hdf(flagged_by_pressor_path, "pressors", mode="w", format="table")
  else:
    break


# save output
print("Saving output to",flagged_by_pressor_path)
ce.ICUSTAY_ID = ce.ICUSTAY_ID.astype(int)
ce.to_hdf(flagged_by_pressor_path, "pressors", mode="w", format="table")

print("Done flagging pressor times!")
print()
