import pandas as pd
import os
import sqlalchemy
import sklearn
import pickle
import numpy as np
import directories
import directories
import feature_definitions


RECORD_LENGTH_HOURS = 12 # how many hours the lab data is accumulated over
RECORD_LENGTH_SHIFT = 6 # how many hours each window is shifted by


def extract_lab_records():
    directories.print_log("\textracting lab records for", RECORD_LENGTH_HOURS,\
        "hr windows, with a shift of", RECORD_LENGTH_SHIFT, "hrs")
    labs = []
    with directories.engine.connect() as connection:
        for k in range(int(48/RECORD_LENGTH_SHIFT)):
            directories.print_log("\t\tloading epoch",k)
            temp = []
            for i in range(RECORD_LENGTH_HOURS):
                QUERY = f"""
                select *
                from lab_events
                where "HOURS_BEFORE_PRESSOR"={RECORD_LENGTH_SHIFT*k + 1 +i}
                order by "HOURS_BEFORE_PRESSOR"
                """
                temp.append(pd.read_sql_query(QUERY, con=connection))
            labs.append(pd.concat(temp))
    return labs


def build_features(labs, pressors_by_icustay):
    directories.print_log("\tbuilding features")
    data = []
    for i in range(len(labs)):
        directories.print_log("\t\tfor epoch", i)
        temp = feature_definitions.attach_lab_features(pressors_by_icustay, labs[i])
        temp["LABEL"] = (temp.EPISODE==1) & (RECORD_LENGTH_SHIFT*i <= 24) # positive detection is 12 hours or less
        temp["EPOCH"] = i
        data.append(temp)
    return pd.concat(data)


def extract_training_inputs(cleaned_data):
    with open(os.path.join(directories.model_dir,"training_subjects.p"),"rb") as file:
        training_subjects = pickle.load(file).values
    training_subjects = training_subjects.reshape(-1,)

    training_inputs = cleaned_data[cleaned_data.SUBJECT_ID.isin(training_subjects)]
    training_inputs = training_inputs[["LABEL","SUBJECT_ID","EPISODE","EPOCH","HADM_ID"] + feature_definitions.features_to_keep]

    ratio = 100.*sum(training_inputs.LABEL.values)/len(training_inputs)
    directories.print_log("\t\t",len(training_inputs),"training samples before dropping na,","%2.0f%%"% ratio,"are positive)")
    training_inputs = training_inputs.dropna()
    training_inputs = training_inputs[training_inputs.EPOCH.isin([0,2,4,6,8])]

    ratio = 100.*sum(training_inputs.LABEL.values)/len(training_inputs)
    directories.print_log("\t\t",len(training_inputs),"training samples after dropping na,","%2.0f%%"% ratio,"are positive)")

    print("\t%2.0f%% of training subjects will need pressors" % (100*sum(training_inputs.EPISODE==1)/len(training_inputs)))
    print("\t%2.0f%% of training subjects won't need pressors at all" % (100*sum(training_inputs.EPISODE==0)/len(training_inputs)))

    directories.print_log("\tsaving features")
    with open(os.path.join(directories.model_dir,"training_features.p"),"wb") as file:
        pickle.dump(training_inputs, file)


def extract_test_inputs(cleaned_data):
    with open(os.path.join(directories.model_dir,"test_subjects.p"),"rb") as file:
        test_subjects = pickle.load(file).values
    test_subjects = test_subjects.reshape(-1,)

    test_inputs = cleaned_data[cleaned_data.SUBJECT_ID.isin(test_subjects)]
    test_inputs = test_inputs[["LABEL","SUBJECT_ID","EPISODE","EPOCH","HADM_ID"] + feature_definitions.features_to_keep]

    ratio = 100.*sum(test_inputs.LABEL.values)/len(test_inputs)
    directories.print_log("\t\t",len(test_inputs),"test samples before dropping na,","%2.0f%%"% ratio,"are positive)")
    test_inputs = test_inputs.dropna()

    ratio = 100.*sum(test_inputs.LABEL.values)/len(test_inputs)
    directories.print_log("\t\t",len(test_inputs),"test samples after dropping na,","%2.0f%%"% ratio,"are positive)")

    print("\t%2.0f%% of test subjects will need pressors" % (100*sum(test_inputs.EPISODE==1)/len(test_inputs)))
    print("\t%2.0f%% of test subjects won't need pressors at all" % (100*sum(test_inputs.EPISODE==0)/len(test_inputs)))

    with open(os.path.join(directories.model_dir,"test_features.p"),"wb") as file:
        pickle.dump(test_inputs, file)


def main():
    directories.print_log("building features")
    labs = extract_lab_records()

    with directories.engine.connect() as connection:
        pressors_by_icustay = pd.read_sql("pressors_by_icustay", con=connection)

    data = build_features(labs, pressors_by_icustay)

    directories.print_log("\tcleaning features")
    cleaned_data = feature_definitions.clean_data(data)
    # set nan flags to zero, since there were no lab results at all in those windows
    cleaned_data.TOTAL_FLAG_COUNT.fillna(0,inplace=True)
    for feature in feature_definitions.features:
        cleaned_data[feature_definitions.features[feature]["ab"]+"_FLAG_COUNT"].fillna(0,inplace=True)

    extract_training_inputs(cleaned_data)

    extract_test_inputs(cleaned_data)

    directories.print_log("done building features!")
    directories.print_log()


# execute only if run as a script
if __name__ == "__main__":
    main()
