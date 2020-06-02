from definitions import *

# extubation event recorded on Metavision
def metavision_extubation(row):
    return row["ITEMID"] in [227194, 225468, 225477]


# mechanical ventilation status from CHARTEVENTS
def mechanical_vent(row):
    itemid = row["ITEMID"]
    value = row["VALUE"]
    return (itemid == 720 and value != "Other/Remarks") or \
(itemid == 223848 and value != "Other") or \
(itemid == 223849) or \
(itemid == 467 and value == "Ventilator") or \
(row["ITEMID"] in ventids)


# oxygen therapy status from CHARTEVENTS
def oxygen_therapy(row):
    return row["ITEMID"] in oxygenids and \
row["VALUE"] in oxygenvals


# extubation status from CHARTEVENTS
def extubation(row):
    return row["ITEMID"] in extubatedids and \
row["VALUE"] in extubatedvals


# self-extubation status from CHARTEVENTS
def self_extubation(row):
    return row["ITEMID"] in selfextubatedids and \
row["VALUE"] in selfextubatedvals


# notable ventilation status
def relevant(row):
    return mechanical_vent(row) or \
oxygen_therapy(row) or \
extubation(row) or \
self_extubation(row)
