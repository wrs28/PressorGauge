import pandas as pd
import os
from sqlalchemy import create_engine

from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables, definitions


##############  definitions ###############

# D_CPT
print("Reading CPT dictionary")
path = os.path.join(mimic_dir, definitions["cpt"] + ".csv")
d_cpt = pd.read_csv(path)
path = os.path.join(processed_data_dir, "rest.h5")
d_cpt.to_hdf(path, "d_cpt", mode="w", format="table")

# D_ICD_DIAGNOSES
print("Reading ICD diagnosis dictionary")
path = os.path.join(mimic_dir, definitions["icd_diagnoses"] + ".csv")
d_icd_d = pd.read_csv(path)
path = os.path.join(processed_data_dir, "rest.h5")
d_icd_d.to_hdf(path, "d_icd_diagnoses", mode="a", format="table")

# D_ICD_PROCEDURES
print("Reading ICD procedures dictionary")
path = os.path.join(mimic_dir, definitions["icd_procedures"] + ".csv")
d_icd_p = pd.read_csv(path)
path = os.path.join(processed_data_dir, "rest.h5")
d_icd_p.to_hdf(path, "d_icd_procedures", mode="a", format="table")

# D_ITEMS
print("Reading items dictionary")
path = os.path.join(mimic_dir, definitions["items"] + ".csv")
d_items = pd.read_csv(path)
path = os.path.join(processed_data_dir, "rest.h5")
d_items.to_hdf(path, "d_items", mode="a", format="table")

# D_LABITEMS
print("Reading labitems dictionary")
path = os.path.join(mimic_dir, definitions["labitems"] + ".csv")
d_labitems = pd.read_csv(path)
path = os.path.join(processed_data_dir, "rest.h5")
d_labitems.to_hdf(path, "d_labitems", mode="a", format="table")


################# non-chart data ##################

# load in ventilation times
print("Reading ventilation episodes")
path = os.path.join(processed_data_dir, "ventilation_times.h5")
vent_episodes = pd.read_hdf(path, "vents")

# ICUSTAYS
print("Process icustays")
path = os.path.join(mimic_dir, tables["icustays"] + ".csv")
icu = pd.read_csv(path, parse_dates = ["INTIME","OUTTIME"])
icu = icu[icu["ICUSTAY_ID"].isin(vent_episodes["ICUSTAY_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
icu.to_hdf(path, "icustays", mode="a", format="table")

# ADMISSIONS
print("Process admissions")
path = os.path.join(mimic_dir, tables["admissions"] + ".csv")
adm = pd.read_csv(path, parse_dates = ["ADMITTIME","DISCHTIME","DEATHTIME","EDREGTIME","EDOUTTIME"])
adm = adm[adm["HADM_ID"].isin(icu["HADM_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
adm.to_hdf(path, "admissions", mode="a", format="table")

# CALLOUT
print("Process callout")
path = os.path.join(mimic_dir, tables["callout"] + ".csv")
callout = pd.read_csv(path, parse_dates = ["CREATETIME","UPDATETIME","ACKNOWLEDGETIME","OUTCOMETIME","FIRSTRESERVATIONTIME","CURRENTRESERVATIONTIME"])
callout = callout[callout["HADM_ID"].isin(adm["HADM_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
callout.to_hdf(path, "callout", mode="a", format="table")

# CPTEVENTS
print("Process cpt events")
path = os.path.join(mimic_dir, tables["cptevents"] + ".csv")
dtypes = {
  "CPT_CD" : str,
  "CPT_SUFFIX" : str,
  "SUBSECTIONHEADER" : str,
  "DESCRIPTION" : str,
}
cpt = pd.read_csv(path, parse_dates = ["CHARTDATE"], dtype=dtypes)
cpt = cpt[cpt["HADM_ID"].isin(adm["HADM_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
cpt.to_hdf(path, "cptevents", mode="a", format="table")

# PATIENTS
print("Process patients")
path = os.path.join(mimic_dir, tables["patients"] + ".csv")
pat = pd.read_csv(path, parse_dates = ["DOB","DOD","DOD_HOSP","DOD_SSN"])
pat = pat[pat["SUBJECT_ID"].isin(adm["SUBJECT_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
pat.to_hdf(path, "patients", mode="a", format="table")

# PROCEDURES_ICD
print("Process icd procedures")
path = os.path.join(mimic_dir, tables["procedures_icd"] + ".csv")
picd = pd.read_csv(path)
picd = picd[picd["SUBJECT_ID"].isin(adm["SUBJECT_ID"])]
path = os.path.join(processed_data_dir, "rest.h5")
picd.to_hdf(path, "procedures_icd", mode="a", format="table")


print("Done processing mimic records!")
