import pandas as pd
import os
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables

dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "vasonum" : pd.Int16Dtype(),
  "duration_hours" : float,
}

path = os.path.join(mimic_dir, "vasopressordurations.csv")
vaso_episodes = pd.read_csv(path, dtype=dtypes,  parse_dates = ["starttime", "endtime"])
vaso_episodes.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "vasonum"        : "EPISODE",
    "starttime"      : "STARTTIME",
    "endtime"        : "ENDTIME",
    "duration_hours" : "DURATION_HOURS"
})


vaso_episodes.dropna(axis=0,inplace=True) # 34 na icustays
number_of_episodes = vaso_episodes[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
vaso_episodes = vaso_episodes.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")


vaso_episodes.ICUSTAY_ID = vaso_episodes.ICUSTAY_ID.astype(int)
vaso_episodes.EPISODE = vaso_episodes.EPISODE.astype(int)
vaso_episodes.STARTTIME = vaso_episodes.STARTTIME.dt.tz_localize(None)
vaso_episodes.ENDTIME = vaso_episodes.ENDTIME.dt.tz_localize(None)


path = os.path.join(processed_data_dir, "vaso_episodes.h5")
vaso_episodes.to_hdf(path, "vaso_episodes", format="table", mode="w")
