N_WINDOWS = 48

import pandas as pd
import progressbar
import sqlalchemy

engine = sqlalchemy.create_engine('postgres://wrs:wrs@localhost/PressorGauge')
with engine.connect() as connection:
  vaso_episodes = pd.read_sql("pressors_by_icustay", con=connection, index_col="ICUSTAY_ID")

print("building hour-long intervals for each icustay")

interval_splits = [pd.Series(vaso_episodes.PRESSOR_START_SEC - i*60*60,name=i, dtype=pd.Int32Dtype()) for i in range(N_WINDOWS+1)]
interval_splits = pd.concat(interval_splits, axis=1)
interval_splits = interval_splits.join(vaso_episodes[["SUBJECT_ID","HADM_ID"]])

print("\tsaving intervals to database `PressorGauge` in table `intervals`")
with engine.connect() as connection:
  interval_splits.to_sql("interval_splits", con=connection, if_exists="replace", index_label="ICUSTAY_ID")

print("Done computing intervals!")
print()
