import os
import pandas as pd
import pickle
import numpy as np
from sklearn import preprocessing, impute
import directories


RND_SEED = 1729


def preprocess_training_inputs():
    with open(os.path.join(directories.model_dir,"training_features.p"),"rb") as file:
        training_inputs = pickle.load(file)

    # ground truth
    training_outputs = training_inputs.pop("LABEL")

    # encode F/M as 1/0
    enc = preprocessing.OrdinalEncoder().fit(pd.DataFrame(training_inputs.GENDER))
    training_inputs.GENDER = enc.transform(pd.DataFrame(training_inputs.GENDER))

    # extract epoch (number of 6-hr windows away from pressor event)
    # and patient-tag indicating pressor nor not (observed label)
    # and subject ID
    training_times = training_inputs.pop("EPOCH")
    pressor_at_all = training_inputs.pop("EPISODE")
    pressor_at_all = pressor_at_all==1
    training_groups = training_inputs.pop("SUBJECT_ID").values
    hadm_id = training_inputs.pop("HADM_ID")

    scaler = preprocessing.StandardScaler().fit(training_inputs)
    with open(os.path.join(directories.model_dir,"scaler_encoder.p"), "wb") as file:
        pickle.dump({"scaler": scaler,"encoder": enc}, file)

    X = training_inputs
    X = pd.DataFrame(X,columns=training_inputs.columns)
    X["EPOCH"] = training_times.values
    X["PRESSOR_AT_ALL"] = pressor_at_all.values
    X["SUBJECT_ID"] = training_groups
    X["HADM_ID"] = hadm_id.values

    y = training_outputs.values.astype(int)

    with open(os.path.join(directories.model_dir,"training_set.p"),"wb") as file:
        pickle.dump({"X": X, "y": y, "cv_groups": training_groups}, file)


def preprocess_tests_inputs():
    with open(os.path.join(directories.model_dir, "test_features.p"),"rb") as file:
        test_inputs = pickle.load(file)

    # ground truth
    test_outputs = test_inputs.pop("LABEL")

    # encode F/M as 1/0
    with open(os.path.join(directories.model_dir, "scaler_encoder.p"), "rsb") as file:
        dict = pickle.load(file)
    enc = dict["encoder"]
    test_inputs.GENDER = enc.transform(pd.DataFrame(test_inputs.GENDER))

    # extract epoch (number of 6-hr windows away from pressor event)
    # and patient-tag indicating pressor nor not (observed label)
    # and subject ID
    test_times = test_inputs.pop("EPOCH")
    pressor_at_all = test_inputs.pop("EPISODE")
    pressor_at_all = pressor_at_all==1
    test_groups = test_inputs.pop("SUBJECT_ID").values
    hadm_id = test_inputs.pop("HADM_ID")

    X = test_inputs
    X = pd.DataFrame(X,columns=test_inputs.columns)
    X["EPOCH"] = test_times.values
    X["PRESSOR_AT_ALL"] = pressor_at_all.values
    X["SUBJECT_ID"] = test_groups
    X["HADM_ID"] = hadm_id.values

    y = test_outputs.values.astype(int)

    with open(os.path.join(directories.model_dir,"test_set.p"),"wb") as file:
        pickle.dump({"X": X, "y": y, "cv_groups": test_groups}, file)


def main():
    directories.print_log("preprocessing data")
    directories.print_log("\tpreparing training set")
    preprocess_training_inputs()
    directories.print_log("\tpreparing test set")
    preprocess_test_inputs()
    directories.print_log("done preprocessing data!")
    directories.print_log()


# execute only if run as a script
if __name__ == "__main__":
    main()
