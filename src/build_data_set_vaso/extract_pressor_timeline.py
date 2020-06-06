import pandas as pd
import os

from directories import project_dir, processed_data_dir, mimic_dir
from definitions import tables, pressor_ids
import vaso_filters

# hdf file name that will store results
flagged_by_pressor_path = os.path.join(processed_data_dir, "flagged_by_pressor.h5")

# hdf file name that will store results
pressor_times_path = os.path.join(processed_data_dir, "pressor_times.h5")


# read in pressor times
ce = pd.read_hdf(flagged_by_pressor_path, "pressors")
nrows = len(ce)
ce.sort_values(by="STARTTIME", inplace=True)


# find first true element in boolean array
def find_first(arr):
  idx = arr.argmax()
  if arr[idx]:
    return idx
  else:
    return len(arr) - 1


print("Finding first pressor times")
dict_list = []
row_pointer = 0
for icustay, group in ce.groupby("ICUSTAY_ID"):
  group = group.sort_values(by="STARTTIME")
  dict_list.append({
    "ICUSTAY_ID" : icustay,
    "STARTTIME"  : group.STARTTIME.iloc[find_first(group.PRESSOR.values)],
  })
  row_pointer += len(group)
  if len(dict_list) % 5 == 0:
    print("\tprocessed", row_pointer, "rows of", nrows)


pressor_times = pd.DataFrame.from_dict(dict_list)


print("Saving ventilation episodes to", pressor_times_path)
pressor_times.to_hdf(pressor_times_path, "pressors", mode="w", format="table")


print("Done processing ventilation times!")
print()
