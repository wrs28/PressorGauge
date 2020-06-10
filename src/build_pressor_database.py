MAXIMUM_ICU_DAYS = 15.
MINIMUM_AGE = 18.
MINIMUM_PRESSOR_DURATION_MINUTES = 15.
MAXIMUM_WEIGHT_KG = 350

import pandas as pd
import os
import numpy as np
import sqlalchemy
from sklearn.neighbors import KernelDensity
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables

print("building pressor database")

## load in isustay data
path = os.path.join(mimic_dir, "ICUSTAYS.csv")
dtypes = {
  "ICUSTAY_ID" : pd.Int32Dtype(),
  "SUBJECT_ID" : pd.Int32Dtype(),
  "HADM_ID" : pd.Int32Dtype(),
}
icustays = pd.read_csv(path, usecols=["ICUSTAY_ID","INTIME","OUTTIME","SUBJECT_ID","HADM_ID"], parse_dates = ["INTIME","OUTTIME"], dtype=dtypes)
icustays;

## append admission data
path = os.path.join(mimic_dir, "ADMISSIONS.csv")
adm = pd.read_csv(path, parse_dates = ["ADMITTIME","DISCHTIME","DEATHTIME","EDREGTIME","EDOUTTIME"])
icustays = icustays.join(adm[["HADM_ID","ADMITTIME","ADMISSION_TYPE","ETHNICITY"]].set_index("HADM_ID"),on="HADM_ID", how="left")
icustays;

## append patient data
path = os.path.join(mimic_dir, "PATIENTS.csv")
pat = pd.read_csv(path, parse_dates = ["DOB","DOD","DOD_HOSP","DOD_SSN"])
icustays = icustays.join(pat[["SUBJECT_ID","GENDER","DOB"]].set_index("SUBJECT_ID"),on="SUBJECT_ID", how="left")
admittime = icustays.ADMITTIME - pd.to_datetime("2000-1-1")
dob = pd.to_datetime("2000-1-1") - icustays.DOB
icustays["AGE"] = round((admittime.dt.days + dob.dt.days)/365).astype(int)
icustays;

## append weight
path = os.path.join(mimic_dir, "heightweight.csv")
heightweight = pd.read_csv(path, dtype={"icustay_id" : pd.Int32Dtype()}, usecols=["icustay_id", "weight_min"])
heightweight.rename(inplace=True, columns = {"icustay_id" : "ICUSTAY_ID", "weight_min" : "WEIGHT_KG"})
length_before_drop = len(heightweight)
heightweight = heightweight[heightweight.WEIGHT_KG < MAXIMUM_WEIGHT_KG]
length_after_drop = len(heightweight)
print("\t",length_before_drop-length_after_drop,"icustays w/ weight greater than",MAXIMUM_WEIGHT_KG,"kg (likely mislabeled)")
icustays = icustays.join(heightweight.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
# icustays[pd.isna(icustays.WEIGHT_KG)]
## append LODS (logistic organ dysfunction score)
path = os.path.join(mimic_dir, "lods.csv")
dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "LODS" : pd.Int16Dtype(),
  "pulmonary" : pd.Int16Dtype(),
  "cardiovascular" : pd.Int16Dtype(),
}
lods = pd.read_csv(path, dtype=dtypes)
lods.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "pulmonary"      : "PULMONARY_LODS",
    "cardiovascular" : "CARDIOVASCULAR_LODS"
})
length_before_drop = len(lods)
lods.dropna(axis=0,inplace=True) # 2482 na icustays
length_after_drop = len(lods)
print("\t",length_before_drop-length_after_drop,"icustays w/o LODS")
lods.ICUSTAY_ID = lods.ICUSTAY_ID.astype(int)
lods.LODS = lods.LODS.astype(int)
lods.PULMONARY_LODS = lods.PULMONARY_LODS.astype(int)
lods.CARDIOVASCULAR_LODS = lods.CARDIOVASCULAR_LODS.astype(int)
icustays = icustays.join(lods.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
icustays;


## append OASIS (Oxford Acute Severity of Illness Score)
path = os.path.join(mimic_dir, "oasis.csv")
dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "OASIS" : pd.Int16Dtype(),
}
oasis = pd.read_csv(path, dtype=dtypes)
oasis.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
})
length_before_drop = len(oasis)
oasis.dropna(axis=0,inplace=True) # 0 na icustays
length_after_drop = len(oasis)
print("\t",length_before_drop-length_after_drop,"icustays w/o OASIS")
oasis.ICUSTAY_ID = oasis.ICUSTAY_ID.astype(int)
oasis.OASIS = oasis.OASIS.astype(int)
icustays = icustays.join(oasis.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
icustays;


## append APACHE scores (acute and chronic health evaluation)
path = os.path.join(mimic_dir, "apache.csv")
dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "APSIII" :  pd.Int16Dtype(),
}
apache = pd.read_csv(path, dtype=dtypes)
apache.rename(inplace=True,
  columns = {
    "icustay_id" : "ICUSTAY_ID",
    "APSIII" : "APACHE"
})
length_before_drop = len(apache)
apache.dropna(axis=0,inplace=True) # 34 na icustays
length_after_drop = len(apache)
print("\t",length_before_drop-length_after_drop,"icustays w/o APACHE")
apache.ICUSTAY_ID = apache.ICUSTAY_ID.astype(int)
apache.APACHE = apache.APACHE.astype(int)
icustays = icustays.join(apache.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
icustays;


## load in vasopressor durations
path = os.path.join(mimic_dir, "vasopressordurations.csv")
dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "vasonum" : pd.Int16Dtype(),
  "duration_hours" : float,
}
vaso_episodes_orig = pd.read_csv(path, dtype=dtypes,  parse_dates = ["starttime", "endtime"])
vaso_episodes_orig.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "vasonum"        : "EPISODE",
    "starttime"      : "STARTTIME",
    "endtime"        : "ENDTIME",
    "duration_hours" : "DURATION_HOURS"
})
# vaso_episodes_orig.dropna(axis=0,inplace=True) # just in case
vaso_episodes_orig;

## add total number of episodes and format dates, keep only the first episode
number_of_episodes = vaso_episodes_orig[["ICUSTAY_ID"]].groupby(["ICUSTAY_ID"]).size().to_frame("NUMBER_OF_EPISODES").reset_index()
vaso_episodes = vaso_episodes_orig.join(number_of_episodes.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="left")
vaso_episodes = vaso_episodes[vaso_episodes.EPISODE == 1]
icustays_bool = (vaso_episodes.groupby("ICUSTAY_ID").size() == 1).values
unique_icustays = vaso_episodes.groupby("ICUSTAY_ID").size().index.values[icustays_bool]
vaso_episodes = vaso_episodes[vaso_episodes.ICUSTAY_ID.isin(unique_icustays)]
vaso_episodes.STARTTIME = vaso_episodes.STARTTIME.dt.tz_localize(None)
vaso_episodes.ENDTIME = vaso_episodes.ENDTIME.dt.tz_localize(None)
vaso_episodes;

## pair episode data with icustay data
vaso_episodes = vaso_episodes.join(icustays.set_index("ICUSTAY_ID"), on="ICUSTAY_ID", how="right")
vaso_episodes;

## for patients with no pressor episodes, set EPISODE, NUMBER_OF_EPISODES, DURATION_HOURS to 0
# vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),"STARTTIME"] = vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),"OUTTIME"]
# vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),"ENDTIME"] = vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),"OUTTIME"]
vaso_episodes.loc[pd.isna(vaso_episodes.EPISODE),["EPISODE","NUMBER_OF_EPISODES","DURATION_HOURS"]] = 0

## compute how long after beginning of ICU stay pressor was administered
vaso_episodes["EPISODE_START_POST_TRANSFER"] = vaso_episodes.STARTTIME - vaso_episodes.INTIME
rows_to_remove = vaso_episodes.EPISODE_START_POST_TRANSFER > pd.Timedelta(days=MAXIMUM_ICU_DAYS)
print("\tdropping",sum(rows_to_remove),"icustays with first pressor episode occurring more than", "%2i"% MAXIMUM_ICU_DAYS,"days after admission")
vaso_episodes = vaso_episodes[~rows_to_remove]
vaso_episodes;

## clean up
vaso_episodes.reset_index(inplace=True)
vaso_episodes.ICUSTAY_ID = vaso_episodes.ICUSTAY_ID.astype(int)
vaso_episodes.EPISODE = vaso_episodes.EPISODE.astype(int)
vaso_episodes.NUMBER_OF_EPISODES = vaso_episodes.NUMBER_OF_EPISODES.astype(int)

## pick start time distribution among patients with no pressors that is represtantive of pressor population
n_no_pressors = sum(vaso_episodes.EPISODE==0)
kde = KernelDensity(kernel="tophat")
kde.fit(np.reshape(vaso_episodes[vaso_episodes.EPISODE==1]["EPISODE_START_POST_TRANSFER"].values.astype(int)/10**9/60/60,(-1,1))) # in hours
times = pd.Series(name="EPISODE_START_POST_TRANSFER", data = np.reshape(kde.sample(n_samples=n_no_pressors,random_state=0),(-1)))
times = pd.to_timedelta(times, unit="hours")
vaso_episodes.loc[vaso_episodes.EPISODE==0, "EPISODE_START_POST_TRANSFER"] = times.values
vaso_episodes.loc[vaso_episodes.EPISODE==0, "STARTTIME"] = vaso_episodes.loc[vaso_episodes.EPISODE==0, "INTIME"] + vaso_episodes.loc[vaso_episodes.EPISODE==0, "EPISODE_START_POST_TRANSFER"]

## repeat for those whose new starttimes are after outtime
needs_fixing = vaso_episodes.STARTTIME > vaso_episodes.OUTTIME
n_no_pressors_new = sum(needs_fixing)
n_no_pressors_new # ~5507
times = pd.Series(name="EPISODE_START_POST_TRANSFER", data = np.reshape(kde.sample(n_samples=n_no_pressors_new,random_state=0),(-1)))
times = pd.to_timedelta(times, unit="hours")
vaso_episodes.loc[needs_fixing, "EPISODE_START_POST_TRANSFER"] = times.values
vaso_episodes.loc[needs_fixing, "STARTTIME"] = vaso_episodes.loc[needs_fixing, "INTIME"] + vaso_episodes.loc[needs_fixing, "EPISODE_START_POST_TRANSFER"]

## repeat for those whose new starttimes are after outtime
needs_fixing = vaso_episodes.STARTTIME > vaso_episodes.OUTTIME
n_no_pressors_new = sum(needs_fixing)
n_no_pressors_new # 1645
times = pd.Series(name="EPISODE_START_POST_TRANSFER", data = np.reshape(kde.sample(n_samples=n_no_pressors_new,random_state=0),(-1)))
times = pd.to_timedelta(times, unit="hours")
vaso_episodes.loc[needs_fixing, "EPISODE_START_POST_TRANSFER"] = times.values
vaso_episodes.loc[needs_fixing, "STARTTIME"] = vaso_episodes.loc[needs_fixing, "INTIME"] + vaso_episodes.loc[needs_fixing, "EPISODE_START_POST_TRANSFER"]

rows_to_remove = vaso_episodes.STARTTIME > vaso_episodes.OUTTIME
print("\tdropping",sum(rows_to_remove),"icustays with pressor start time after icustay endtime")
vaso_episodes = vaso_episodes[~rows_to_remove]
vaso_episodes;


## clean up ICU stays
rows_to_replace = vaso_episodes.AGE > 150
print("\treplacing age of",sum(rows_to_replace),"patients over 89 with age 91")
vaso_episodes.loc[rows_to_replace, "AGE"] = 91
rows_to_remove = vaso_episodes.AGE < MINIMUM_AGE
print("\tdropping",sum(rows_to_remove),"icustays with age less than", MINIMUM_AGE)
vaso_episodes = vaso_episodes[~rows_to_remove]

rows_to_remove = (vaso_episodes.DURATION_HOURS < MINIMUM_PRESSOR_DURATION_MINUTES/60) & (vaso_episodes.EPISODE==1)
print("\tdropping",sum(rows_to_remove),"pressor episodes with vaso durations less than", MINIMUM_PRESSOR_DURATION_MINUTES,"minutes")
vaso_episodes = vaso_episodes[~rows_to_remove]

vaso_episodes.set_index("ICUSTAY_ID", inplace=True)

# vaso_episodes.reset_index(inplace=True)
vaso_episodes["PRESSOR_START_SEC"] = ((vaso_episodes.STARTTIME - vaso_episodes.INTIME).astype(int)/10**9).apply(np.int32)
labels = [
  "index",
  "ENDTIME",
  "DURATION_HOURS",
  "NUMBER_OF_EPISODES",
  # "INTIME",
  "OUTTIME",
  "EPISODE_START_POST_TRANSFER",
  "ADMITTIME",
  "STARTTIME",
  "DOB"
]
vaso_episodes.drop(axis=1,labels=labels, inplace=True)

len1 = len(vaso_episodes)
vaso_episodes.dropna(inplace=True)
len2 = len(vaso_episodes)
print("\tdropping",len1-len2,"icustays with missing values")

print("\tdropping",len(vaso_episodes) - len(vaso_episodes.HADM_ID.unique()),"multiple ICU stays in same hospital visit")
vaso_episodes.drop_duplicates("HADM_ID", inplace=True)


engine = sqlalchemy.create_engine('postgres://wrs:wrs@localhost/PressorGauge')

print("\tsaving to SQL database `PressorGauge`, table `pressors_by_icustay`")
with engine.connect() as connection:
  vaso_episodes.to_sql("pressors_by_icustay", con=connection, if_exists="replace", index_label="ICUSTAY_ID")

print("\ttotal of",len(vaso_episodes),"icustays, of which",sum(vaso_episodes.EPISODE>0),"have a pressor episode")
check = 100*float(sum(vaso_episodes.EPISODE==1))/len(vaso_episodes)
print("\tsanity check: %2.0f%%" % check,"have pressors, ideally in range 1/4 to 1/3")

print("Done building pressor database!")
print()
