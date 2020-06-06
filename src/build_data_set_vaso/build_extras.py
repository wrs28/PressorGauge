import pandas as pd
import os
from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables


dtypes = {
  "icustay_id" : pd.Int32Dtype(),
}

path = os.path.join(mimic_dir, "heightweight.csv")
heightweight = pd.read_csv(path, dtype=dtypes, usecols=["icustay_id", "weight_min"])
heightweight.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "weight_min"   : "WEIGHT",
})


heightweight.dropna(axis=0, inplace=True) # 34 na icustays
heightweight.ICUSTAY_ID = heightweight.ICUSTAY_ID.astype(int)

path = os.path.join(processed_data_dir, "extras.h5")
heightweight.to_hdf(path, "weight", format="table", mode="w")




dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "LODS" : pd.Int16Dtype(),
  "pulmonary" : pd.Int16Dtype(),
  "cardiovascular" : pd.Int16Dtype(),
}

path = os.path.join(mimic_dir, "lods.csv")
lods = pd.read_csv(path, dtype=dtypes)
lods.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
    "pulmonary"      : "PULMONARY",
    "cardiovascular" : "CARDIOVASCULAR"
})


lods.dropna(axis=0,inplace=True) # 34 na icustays
lods.ICUSTAY_ID = lods.ICUSTAY_ID.astype(int)
lods.LODS = lods.LODS.astype(int)
lods.PULMONARY = lods.PULMONARY.astype(int)
lods.CARDIOVASCULAR = lods.CARDIOVASCULAR.astype(int)

path = os.path.join(processed_data_dir, "extras.h5")
lods.to_hdf(path, "lods", format="table", mode="a")




dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "OASIS" : pd.Int16Dtype(),
}

path = os.path.join(mimic_dir, "oasis.csv")
oasis = pd.read_csv(path, dtype=dtypes)
oasis.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
})


oasis.dropna(axis=0,inplace=True) # 34 na icustays
oasis.ICUSTAY_ID = oasis.ICUSTAY_ID.astype(int)
oasis.OASIS = oasis.OASIS.astype(int)


path = os.path.join(processed_data_dir, "extras.h5")
oasis.to_hdf(path, "oasis", format="table", mode="a")








dtypes = {
  "icustay_id" : pd.Int32Dtype(),
  "APSIII" : pd.Int16Dtype(),
}

path = os.path.join(mimic_dir, "apache.csv")
apache = pd.read_csv(path, dtype=dtypes)
apache.rename(inplace=True,
  columns = {
    "icustay_id"     : "ICUSTAY_ID",
})


apache.dropna(axis=0,inplace=True) # 34 na icustays
apache.ICUSTAY_ID = apache.ICUSTAY_ID.astype(int)
apache.APSIII = apache.APSIII.astype(int)


path = os.path.join(processed_data_dir, "extras.h5")
apache.to_hdf(path, "apache", format="table", mode="a")
