import pandas as pd
import os
import numpy as np
import sqlalchemy
import pickle
from sklearn.neighbors import KernelDensity
import directories


RND_SEED = 1729
MINIMUM_TIME_TO_PRESSOR_HOURS = 12
MAXIMUM_TIME_TO_PRESSOR_DAYS = 50.
MINIMUM_PRESSOR_DURATION_MINUTES = 15.
MINIMUM_AGE = 18.
MAXIMUM_WEIGHT_KG = 350
MINIMUM_WEIGHT_KG = 25


## load in icustay data
def load_icustay():
    path = os.path.join(directories.mimic_dir, "ICUSTAYS.csv")
    dtypes = {
        "ICUSTAY_ID" : pd.Int32Dtype(),
        "SUBJECT_ID" : pd.Int32Dtype(),
        "HADM_ID" : pd.Int32Dtype(),
    }
    cols = [
        "ICUSTAY_ID",
        "INTIME",
        "OUTTIME",
        "SUBJECT_ID",
        "HADM_ID"
    ]
    date_cols = ["INTIME","OUTTIME"]
    icustays = pd.read_csv(path, usecols=cols, parse_dates=date_cols, dtype=dtypes)
    return icustays


## append admission data
def load_admissions(icustays):
    path = os.path.join(directories.mimic_dir, "ADMISSIONS.csv")
    date_cols = [
        "ADMITTIME",
        "DISCHTIME",
        "DEATHTIME",
        "EDREGTIME",
        "EDOUTTIME"
    ]
    adm = pd.read_csv(path, parse_dates=date_cols)
    icustays = icustays.join(adm[["HADM_ID","ADMITTIME","ADMISSION_TYPE","ETHNICITY"]].set_index("HADM_ID"),on="HADM_ID", how="left")
    return icustays


## append patient data
def load_patients(icustays):
    path = os.path.join(directories.mimic_dir, "PATIENTS.csv")
    date_cols = [
        "DOB",
        "DOD",
        "DOD_HOSP",
        "DOD_SSN"
    ]
    pat = pd.read_csv(path, parse_dates=date_cols)
    icustays = icustays.join(pat[["SUBJECT_ID","GENDER","DOB"]].set_index("SUBJECT_ID"),on="SUBJECT_ID", how="left")
    # for patients older than 89, age is shifted to 300, which is too big for nanosecond integer representation, so pick Jan 1, 2000 as intermediate
    admittime = icustays.ADMITTIME - pd.to_datetime("2000-1-1")
    dob = pd.to_datetime("2000-1-1") - icustays.DOB
    icustays["AGE"] = round((admittime.dt.days + dob.dt.days)/365).astype(int)
    return icustays


## append weight
def load_weights(icustays):
    path = os.path.join(directories.mimic_dir, "heightweight.csv")
    heightweight = pd.read_csv(path, dtype={"icustay_id": pd.Int32Dtype()}, usecols=["icustay_id", "weight_min"])
    heightweight.rename(inplace=True, columns={"icustay_id": "ICUSTAY_ID", "weight_min": "WEIGHT_KG"})
    # print num rows dropped b/c of weight
    length_before_drop = len(heightweight)
    heightweight = heightweight[(MINIMUM_WEIGHT_KG < heightweight.WEIGHT_KG) & \
        (heightweight.WEIGHT_KG < MAXIMUM_WEIGHT_KG)]
    length_after_drop = len(heightweight)
    directories.print_log("\t",length_before_drop-length_after_drop, "icustays w/ weight greater than",\
        MAXIMUM_WEIGHT_KG, "kg (likely mislabeled)")
    icustays = icustays.join(heightweight.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
    return icustays


## append LODS (logistic organ dysfunction score)
def load_LODS(icustays):
    path = os.path.join(directories.mimic_dir, "lods.csv")
    dtypes = {
        "icustay_id" : pd.Int32Dtype(),
        "LODS" : pd.Int16Dtype(),
        "pulmonary" : pd.Int16Dtype(),
        "cardiovascular" : pd.Int16Dtype(),
    }
    lods = pd.read_csv(path, dtype=dtypes)
    lods.rename(
    inplace=True,
    columns = {
        "icustay_id"     : "ICUSTAY_ID",
        "pulmonary"      : "PULMONARY_LODS",
        "cardiovascular" : "CARDIOVASCULAR_LODS"
    }
    )
    # print number of icustays dropped from missing LODS
    length_before_drop = len(lods)
    lods.dropna(axis=0,inplace=True) # 2482 na icustays
    length_after_drop = len(lods)
    directories.print_log("\t",length_before_drop-length_after_drop,"icustays w/o LODS")
    # interpret LODS scores as ints
    lods.ICUSTAY_ID = lods.ICUSTAY_ID.astype(int)
    lods.LODS = lods.LODS.astype(int)
    lods.PULMONARY_LODS = lods.PULMONARY_LODS.astype(int)
    lods.CARDIOVASCULAR_LODS = lods.CARDIOVASCULAR_LODS.astype(int)
    icustays = icustays.join(lods.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
    return icustays


## append OASIS (Oxford Acute Severity of Illness Score)
def load_OASIS(icustays):
    path = os.path.join(directories.mimic_dir, "oasis.csv")
    dtypes = {
        "icustay_id" : pd.Int32Dtype(),
        "OASIS" : pd.Int16Dtype(),
    }
    oasis = pd.read_csv(path, dtype=dtypes)
    oasis.rename(
    inplace=True,
    columns = {
        "icustay_id": "ICUSTAY_ID",
    }
    )
    # print number of icustays dropped from missing OASIS
    length_before_drop = len(oasis)
    oasis.dropna(axis=0,inplace=True) # 0 na icustays
    length_after_drop = len(oasis)
    directories.print_log("\t",length_before_drop-length_after_drop,"icustays w/o OASIS")
    # interpret OASIS scores as int
    oasis.ICUSTAY_ID = oasis.ICUSTAY_ID.astype(int)
    oasis.OASIS = oasis.OASIS.astype(int)
    icustays = icustays.join(oasis.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
    return icustays


## append APACHE scores (acute and chronic health evaluation)
def load_APACHE(icustays):
    path = os.path.join(directories.mimic_dir, "apache.csv")
    dtypes = {
        "icustay_id": pd.Int32Dtype(),
        "APSIII":  pd.Int16Dtype(),
    }
    apache = pd.read_csv(path, dtype=dtypes)
    apache.rename(
    inplace=True,
    columns = {
        "icustay_id" : "ICUSTAY_ID",
        "APSIII" : "APACHE"
    }
    )
    # print number of icustays dropped from missing APACHE
    length_before_drop = len(apache)
    apache.dropna(axis=0,inplace=True) # 34 na icustays
    length_after_drop = len(apache)
    directories.print_log("\t",length_before_drop-length_after_drop,"icustays w/o APACHE")
    # interpret APACHE score as int
    apache.ICUSTAY_ID = apache.ICUSTAY_ID.astype(int)
    apache.APACHE = apache.APACHE.astype(int)
    icustays = icustays.join(apache.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
    return icustays


## load in vasopressor durations
def load_vasopressor_durations():
    path = os.path.join(directories.mimic_dir, "vasopressordurations.csv")
    dtypes = {
        "icustay_id" : pd.Int32Dtype(),
        "vasonum" : pd.Int16Dtype(),
        "duration_hours" : float,
    }
    date_cols = ["starttime", "endtime"]
    vaso_episodes = pd.read_csv(path, dtype=dtypes, parse_dates=date_cols)
    vaso_episodes.rename(
    inplace=True,
    columns = {
        "icustay_id"     : "ICUSTAY_ID",
        "vasonum"        : "EPISODE",
        "starttime"      : "STARTTIME",
        "endtime"        : "ENDTIME",
        "duration_hours" : "DURATION_HOURS"
    }
    )
    # vaso_episodes_orig.dropna(axis=0,inplace=True) # just in case
    return vaso_episodes


## add total number of episodes and format dates, keep only the first episode
def clean_vaso_episodes_1(vaso_episodes):
    number_of_episodes = vaso_episodes[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
    vaso_episodes = vaso_episodes.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
    vaso_episodes = vaso_episodes[vaso_episodes.EPISODE == 1]
    icustays_bool = (vaso_episodes.groupby("ICUSTAY_ID").size() == 1).values
    unique_icustays = vaso_episodes.groupby("ICUSTAY_ID").size().index.values[icustays_bool]
    vaso_episodes = vaso_episodes[vaso_episodes.ICUSTAY_ID.isin(unique_icustays)]
    vaso_episodes.STARTTIME = vaso_episodes.STARTTIME.dt.tz_localize(None)
    vaso_episodes.ENDTIME = vaso_episodes.ENDTIME.dt.tz_localize(None)
    return vaso_episodes


## pair episode data with icustay data
def pair_episodes_and_stays(vaso_episodes, icustays):
    vaso_episodes = vaso_episodes.join(icustays.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="right")
    # for patients with no pressor episodes, set EPISODE, NUMBER_OF_EPISODES, DURATION_HOURS to 0
    vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),["EPISODE","NUMBER_OF_EPISODES","DURATION_HOURS"]] = 0
    return vaso_episodes


## compute how long after beginning of ICU stay pressor was administered
def compute_hours_to_pressor(vaso_episodes):
    vaso_episodes["EPISODE_START_POST_TRANSFER"] = vaso_episodes.STARTTIME - vaso_episodes.ADMITTIME
    rows_to_remove = vaso_episodes.EPISODE_START_POST_TRANSFER > pd.Timedelta(days=MAXIMUM_TIME_TO_PRESSOR_DAYS)
    directories.print_log("\tdropping", sum(rows_to_remove), "icustays with first pressor episode occurring more than", "%2i"% MAXIMUM_TIME_TO_PRESSOR_DAYS, "days after admission")
    vaso_episodes = vaso_episodes[~rows_to_remove]
    return vaso_episodes


## clean up
def clean_vaso_episodes_2(vaso_episodes):
    vaso_episodes.reset_index(inplace=True)
    vaso_episodes.ICUSTAY_ID = vaso_episodes.ICUSTAY_ID.astype(int)
    vaso_episodes.EPISODE = vaso_episodes.EPISODE.astype(int)
    vaso_episodes.NUMBER_OF_EPISODES = vaso_episodes.NUMBER_OF_EPISODES.astype(int)

    vaso_episodes.loc[vaso_episodes.EPISODE==0,"EPISODE_START_POST_TRANSFER"] = (vaso_episodes.OUTTIME - vaso_episodes.ADMITTIME)[vaso_episodes.EPISODE==0]
    vaso_episodes.loc[vaso_episodes.EPISODE==0,"STARTTIME"] = vaso_episodes.OUTTIME[vaso_episodes.EPISODE==0]

    # remove episodes that start in the first day
    sum(vaso_episodes.EPISODE_START_POST_TRANSFER < pd.Timedelta(hours=MINIMUM_TIME_TO_PRESSOR_HOURS))
    rows_to_remove = vaso_episodes.EPISODE_START_POST_TRANSFER < pd.Timedelta(hours=MINIMUM_TIME_TO_PRESSOR_HOURS)
    directories.print_log("\tdropping",sum(rows_to_remove),"icustays with first pressor episode occurring less than", "%2i"% MINIMUM_TIME_TO_PRESSOR_HOURS,"hours after hospital admission")
    vaso_episodes = vaso_episodes[~rows_to_remove].copy()
    len(vaso_episodes)

    ## clean up ICU stays
    rows_to_replace = vaso_episodes.AGE > 150
    directories.print_log("\treplacing age of",sum(rows_to_replace),"patients over 89 with age 91")
    vaso_episodes.loc[rows_to_replace, "AGE"] = 91
    rows_to_remove = vaso_episodes.AGE < MINIMUM_AGE
    directories.print_log("\tdropping",sum(rows_to_remove),"icustays with age less than", MINIMUM_AGE)
    vaso_episodes = vaso_episodes[~rows_to_remove]

    rows_to_remove = (vaso_episodes.DURATION_HOURS < MINIMUM_PRESSOR_DURATION_MINUTES/60) & (vaso_episodes.EPISODE==1)
    directories.print_log("\tdropping",sum(rows_to_remove),"pressor episodes with vaso durations less than", MINIMUM_PRESSOR_DURATION_MINUTES,"minutes")
    vaso_episodes = vaso_episodes[~rows_to_remove]

    vaso_episodes.set_index("ICUSTAY_ID", inplace=True)

    # compute pressor time distribution
    kde_true = KernelDensity(kernel="tophat")
    kde_true.fit(np.reshape(vaso_episodes[vaso_episodes.EPISODE==1]["EPISODE_START_POST_TRANSFER"].values.astype(int)/10**9/60/60,(-1,1))) # in hours
    kde_false = KernelDensity(kernel="tophat")
    kde_false.fit(np.reshape(vaso_episodes[vaso_episodes.EPISODE==0]["EPISODE_START_POST_TRANSFER"].values.astype(int)/10**9/60/60,(-1,1))) # in hours
    with open(os.path.join(directories.model_dir,"time_distributions.p"),"wb") as file:
        pickle.dump({"kde_true" : kde_true, "kde_false" : kde_false},file)

    # vaso_episodes.reset_index(inplace=True)
    vaso_episodes["PRESSOR_START_SEC"] = vaso_episodes.STARTTIME - vaso_episodes.ADMITTIME
    vaso_episodes = vaso_episodes[~vaso_episodes.PRESSOR_START_SEC.isna()]
    vaso_episodes.PRESSOR_START_SEC = (vaso_episodes.PRESSOR_START_SEC.astype(int)/10**9).apply(np.int32)
    labels = [
        "index",
        "ENDTIME",
        "DURATION_HOURS",
        "NUMBER_OF_EPISODES",
        "INTIME",
        "OUTTIME",
        "EPISODE_START_POST_TRANSFER",
        "STARTTIME",
        "DOB"
    ]
    vaso_episodes.drop(axis=1,labels=labels, inplace=True)

    len1 = len(vaso_episodes)
    vaso_episodes.dropna(inplace=True)
    len2 = len(vaso_episodes)
    directories.print_log("\tdropping",len1-len2,"icustays with missing values")

    directories.print_log("\tdropping",len(vaso_episodes) - len(vaso_episodes.HADM_ID.unique()),"multiple ICU stays in same hospital visit")
    vaso_episodes.drop_duplicates("HADM_ID", inplace=True)

    return vaso_episodes


def compute_pressor_time_distribution(vaso_episodes):
    kde_true = KernelDensity(kernel="tophat")
    kde_true.fit(np.reshape(vaso_episodes[vaso_episodes.EPISODE==1]["EPISODE_START_POST_TRANSFER"].values.astype(int)/10**9/60/60,(-1,1))) # in hours
    kde_false = KernelDensity(kernel="tophat")
    kde_false.fit(np.reshape(vaso_episodes[vaso_episodes.EPISODE==0]["EPISODE_START_POST_TRANSFER"].values.astype(int)/10**9/60/60,(-1,1))) # in hours
    with open(os.path.join(directories.model_dir,"time_distributions.p"),"wb") as file:
        pickle.dump({"kde_true" : kde_true, "kde_false" : kde_false},file)


def main():
    directories.print_log("building pressor database",mode="w")
    icustays = load_icustay()
    icustays = load_admissions(icustays)
    icustays = load_patients(icustays)
    icustays = load_weights(icustays)
    icustays = load_LODS(icustays)
    icustays = load_OASIS(icustays)
    icustays = load_APACHE(icustays)

    vaso_episodes = load_vasopressor_durations()
    vaso_episodes = clean_vaso_episodes_1(vaso_episodes)
    vaso_episodes = pair_episodes_and_stays(vaso_episodes, icustays)
    vaso_episodes = compute_hours_to_pressor(vaso_episodes)
    vaso_episodes = clean_vaso_episodes_2(vaso_episodes)

    directories.print_log("\tsaving to SQL database `PressorGauge`, table `pressors_by_icustay`")
    with directories.engine.connect() as connection:
        vaso_episodes.to_sql("pressors_by_icustay", con=connection, if_exists="replace", index_label="ICUSTAY_ID")

    directories.print_log("\ttotal of",len(vaso_episodes),"icustays, of which",sum(vaso_episodes.EPISODE>0),"have a pressor episode")
    check = 100*float(sum(vaso_episodes.EPISODE==1))/len(vaso_episodes)
    directories.print_log("\tsanity check: %2.0f%%" % check,"have pressors, ideally in range 1/4 to 1/3")

    directories.print_log("Done building pressor database!")
    directories.print_log()


# execute only if run as a script
if __name__ == "__main__":
    main()
