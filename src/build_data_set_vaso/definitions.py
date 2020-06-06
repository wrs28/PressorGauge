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

pressor_ids_mv = [
    221906, # Norepinephrine
    221289, # Epinephrine
    222315, # Vasopressin
    221662, # Dopamine
    221749, # Phenylephrine
    221653, # Dobutamine
]

pressor_ids_cv = [
    30044,                # Epinephrine
    30051, 42273, 46570,  # Vasopressin
    30043, 30307,         # Dopamine
    30306, 30042,         # Dobutamine
]

pressor_ids = pressor_ids_mv #+ press_ids_cv
