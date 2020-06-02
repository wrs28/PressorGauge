mimic_dir = "/Volumes/gaia/mimic"

################# DEFINE MIMIC TABLES #########################

tables = {
    "admissions"         : "ADMISSIONS",         # Define a patient’s hospital admission, HADM_ID.
    "callout"            : "CALLOUT",            # When a patient was READY for discharge from the ICU, and when the patient was actually discharged from the ICU
    "caregivers"         : "CAREGIVERS",         # Defines the role of caregivers.
    "chartevents"        : "CHARTEVENTS",        # Contains all charted data for all patients.
    "cptevents"          : "CPTEVENTS",          # Current procedural terminology (CPT) codes, which facilitate billing for procedures performed on patients.
    "datetimeevents"     : "DATETIMEEVENTS",     # Contains all date formatted data
    "diagnoses"          : "DIAGNOSES_ICD",      # Contains ICD diagnoses for patients, most notably ICD-9 diagnoses
    "drg"                : "DRGCODES",           # Contains diagnosis related groups (DRG) codes for patients
    "icustays"           : "ICUSTAYS",           # Defines each ICUSTAY_ID in the database, i.e. defines a single ICU stay.
    "inputevents_cv"     : "INPUTEVENTS_CV",     # CareVue input data for patients (telemetry data)
    "inputevents_mv"     : "INPUTEVENTS_MV",     # Metavision input data for patients (telemetry data)
    "labevents"          : "LABEVENTS",          # Contains all laboratory measurements for a given patient, including out patient data.
    "microbiologyevents" : "MICROBIOLOGYEVENTS", # Contains microbiology information, including cultures acquired and associated sensitivities.
    "noteevents"         : "NOTEEVENTS",         # Contains all notes for patients
    "outputevents"       : "OUTPUTEVENTS",       # Output data for patients (fluids coming out through urine)
    "patients"           : "PATIENTS",           # Defines each SUBJECT_ID in the database, i.e. defines a single patient
    "prescriptions"      : "PRESCRIPTIONS",      # Contains medication related order entries, i.e. prescriptions
    "procedureevents_mv" : "PROCEDUREEVENTS_MV", # Contains procedures for patients
    "procedures_icd"     : "PROCEDURES_ICD",     # Contains ICD procedures for patients, most notably ICD-9 procedures
    "services"           : "SERVICES",           # Lists services that a patient was admitted/transferred under
    "transfers"          : "TRANSFERS",          # Physical locations for patients throughout their hospital stay
}

################# DEFINE MIMIC DEFINITOINS #########################

definitions = {
    "cpt"            : "D_CPT",
    "icd_diagnoses"  : "D_ICD_DIAGNOSES",
    "icd_procedures" : "D_ICD_PROCEDURES",
    "items"          : "D_ITEMS",
    "labitems"       : "D_LABITEMS",
}

################# INTUBATED ITEMIDs #########################

ventids = [
    445, 448, 449, 450, 1340, 1486, 1600, 224687,                     # minute volume
    639, 654, 681, 682, 683, 684, 224685, 224684, 224686,             # tidal volume
    218, 436, 535, 444, 459, 224697, 224695, 224696, 224746, 224747,  # high/low/peak/mean/neg insp force ("RespPressure")
    221, 1, 1211, 1655, 2000, 226873, 224738, 224419, 224750, 227187, # insp pressure
    543,                                                              # Plateau Pressure
    5865, 5866, 224707, 224709, 224705, 224706,                       # APRV pressure
    60, 437, 505, 506, 686, 220339, 224700,                           # PEEP
    3459,                                                             # high pressure relief
    501, 502, 503, 224702,                                            # PCV
    223, 667, 668, 669, 670, 671, 672,                                # TCPCV
    224701,                                                           # PSVlevel
]

################# OXYGEN THERAPY ITEMIDs #########################

oxygenids = [
    467,
    226732,
]

oxygenvals = [
    "Cannula",
    "Cannula ",
    "cannula",
    "cannula "
    "Nasal cannula",
    "Nasal Cannula",
    "Face tent",
    "Face Tent",
    "Aerosol-cool",
    "Aerosol-Cool",
    "Trach mask ",
    "Trach Mask ",
    "High flow neb",
    "High Flow Neb",
    "Non-Rebreather",
    "Venti Mask",
    "Medium Conc Mask",
    "Vapotherm",
    "T-Piece",
    "High flow nasal cannula",
    "Hood",
    "Hut",
    "TranstrachealCat",
    "Heated Neb",
    "Ultrasonic Neb",
    "Vapomist",
]

################## EXTUBATION ITEMIDs ########################

extubatedids = [
    640,
]

extubatedvals = [
    "Extubated",
    "Self Extubation",
]

################## SELF-EXTUBATION ITEMIDs ########################

selfextubatedids = [
    640,
]

selfextubatedvals = [
    "Self Extubation",
]
