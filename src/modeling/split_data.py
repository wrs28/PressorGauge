import pandas as pd
import pickle
import os
from sklearn import model_selection
from directories import print_log, engine, model_dir


RND_SEED = 2 # random seed used throughout
TEST_SIZE_FRACTION = .1 # fraction of data is set aside for testing


def main():
    with engine.connect() as connection:
        pressors_by_icustay = pd.read_sql("pressors_by_icustay", con=connection, index_col="ICUSTAY_ID")

    X = pressors_by_icustay.groupby("SUBJECT_ID").agg({"EPISODE": "max"}).reset_index()
    y = X.pop("EPISODE")

    print_log("splitting train, validation, and test sets",mode="w")
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=TEST_SIZE_FRACTION, random_state=RND_SEED, stratify=y)

    print_log("\t",len(X_train),"training samples")
    print_log("\t",len(X_test),"testing samples")

    print_log("\t saving train and test set identifiers")
    with open(os.path.join(model_dir,"training_subjects.p"), "wb") as file:
        pickle.dump(X_train, file)
    with open(os.path.join(model_dir,"test_subjects.p"), "wb") as file:
        pickle.dump(X_test, file)

    print_log("done splitting data!")
    print_log()


# execute only if run as a script
if __name__ == "__main__":
    main()
