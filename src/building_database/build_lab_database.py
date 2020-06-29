import numpy as np
import pandas as pd
import os
import math
import sqlalchemy
from directories import project_dir, model_dir, mimic_dir, print_log, engine
from definitions import tables


# number of rows in LABEVENTS to read in at a time (there are 27_854_055 lines in LABEVENTS)
CHUNK_SIZE = 10**6
NUM_CHUNKS = np.inf


def find_first(arr):
  idx = arr.argmax()
  if arr[idx]:
    return idx
  else:
    return None


def extract_lab_events(vaso_episodes, interval_splits):
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

    date_cols = ["CHARTTIME"]

    print_log("extracting relevent lab events")
    path = os.path.join(mimic_dir, tables["labevents"] + ".csv")
    count = 0
    replace_flag = True
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=columns, dtype=dtypes, parse_dates=date_cols):
        # add columns to keep track of whether or not 24 hours from pressor (PRESSOR_LABEL)
        # and which hour before pressor event it it (HOURS_BEFORE_PRESSOR)
        chunk = chunk[~pd.isna(chunk.HADM_ID)] # throwing away about 25% of labs from outpatient settings b/c hard to attach them to an admission nubmer
        chunk["HOURS_BEFORE_PRESSOR"] = 0
        temp = chunk.join(vaso_episodes[["HADM_ID","ADMITTIME"]].set_index("HADM_ID"),on="HADM_ID")
        chunk.CHARTTIME = np.int32((chunk.CHARTTIME - temp.ADMITTIME).values/10**9)
        count += 1
        if count > NUM_CHUNKS:
            break
        else:
            print_log("\tprocessing LABEVENTS chunk:",count, "of", math.ceil(27_854_055/CHUNK_SIZE))
            # loop through all the times in a given hospital admission (HADM_ID), recall we keep only hospital admissions with 1 icustay
            for (time, hadm), time_group in chunk[chunk.HADM_ID.isin(vaso_episodes.HADM_ID)].groupby(["CHARTTIME","HADM_ID"]):
                # only extract lab data if it falls in the interval i
                splits = interval_splits.loc[hadm]
                i = find_first((splits[1:-1].values < time) & (time <= splits[:-2].values))
                if i:
                    time_group = time_group.copy()
                    time_group.HOURS_BEFORE_PRESSOR = i
                    # if within one day of pressor event, lable true if episode==1
                    # if first entry to be added, replace table, otherwise add to it
                    if replace_flag:
                        mode = "replace"
                        replace_flag = False
                    else:
                        mode = "append"
                    with engine.connect() as connection:
                        time_group.to_sql("lab_events", con=connection, if_exists=mode, index=False)



def main():
    # load in ventilation times
    with engine.connect() as connection:
        vaso_episodes = pd.read_sql("pressors_by_icustay", con=connection, index_col="ICUSTAY_ID")

    with engine.connect() as connection:
        interval_splits = pd.read_sql("interval_splits", con=connection, index_col="ICUSTAY_ID")

    interval_splits.set_index("HADM_ID", inplace=True)

    extract_lab_events(vaso_episodes, interval_splits)

    print_log("Done processing lab events!")
    print_log()


# execute only if run as a script
if __name__ == "__main__":
    main()
