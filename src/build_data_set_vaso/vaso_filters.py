from definitions import *

# extubation event recorded on Metavision
def pressor(row):
    return row["ITEMID"] in pressor_ids
