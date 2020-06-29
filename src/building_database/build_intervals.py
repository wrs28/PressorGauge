import pandas as pd
import sqlalchemy
from directories import print_log, engine


N_WINDOWS = 48


def main():

    with engine.connect() as connection:
        vaso_episodes = pd.read_sql("pressors_by_icustay", con=connection, index_col="ICUSTAY_ID")

    print_log("building hour-long intervals for each icustay")

    interval_splits = [pd.Series(vaso_episodes.PRESSOR_START_SEC - i*60*60, name=i, dtype=pd.Int32Dtype()) for i in range(N_WINDOWS+1)]
    interval_splits = pd.concat(interval_splits, axis=1)
    interval_splits = interval_splits.join(vaso_episodes[["SUBJECT_ID","HADM_ID"]])

    print_log("\tsaving intervals to database `PressorGauge` in table `intervals`")
    with engine.connect() as connection:
        interval_splits.to_sql("interval_splits", con=connection, if_exists="replace", index_label="ICUSTAY_ID")

    print_log("Done computing intervals!")
    print_log()



# execute only if run as a script
if __name__ == "__main__":
    main()
