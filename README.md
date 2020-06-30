# Pressor Gauge

#### Predicting the need for life-saving blood pressure medication

###### William R. Sweeney, Data Science Insight Fellow, Summer 2020

Pressor Gauge is a [web app](http://pressorgauge.com) designed to help physicians prioritize their care for patients who will soon become very sick and need life-saving blood pressure medication (pressors).

The web app can be found at [pressorgauge.com](http://pressorgauge.com), and the accompanying demo slides can be found [here](https://docs.google.com/presentation/d/1O2QuISdaB0OOj7BF372qH_N30NvK4DMR628YFlL2-XE/edit?usp=sharing).


## Installing

Clone this repository to the current working directory:
````
git clone git@github.com:wrs28/PressorGauge.git
````

Create a Conda environment (it will be called 'PressorGauge'):
````
conda env create -f environment.yml
````

Activate it with
````
conda activate PressorGauge
````

The [MIMIC-III](https://mimic.physionet.org) data are not included, as they require special access, though anyone can request access.
Once access is gained and the data are downloaded, set the `MIMIC_DIR` variable in [`src/building_database/directories.py`](https://github.com/wrs28/PressorGauge/blob/master/src/building_database/directories.py) to the location of the MIMIC-III data.


The shell script [`building_database.sh`](https://github.com/wrs28/PressorGauge/blob/master/build_databases.sh) will build a SQL database locally, as specified in the `engine` variable in [`src/building_database/directories.py`](https://github.com/wrs28/PressorGauge/blob/master/src/building_database/directories.py) (the DB must be created by the user, and `engine` must be accordingly updated).
The other shell script [`building_model.sh`](https://github.com/wrs28/PressorGauge/blob/master/build_model.sh) will clean the data and build the features.
Logs of both scripts are stored in `logs/build.log` and `logs/model.log`.


## Requisites

- conda
- pandas
- numpy
- scipy
- scikit-learn
- psycopg2
- sqlalchemy
- shap
- streamlit
- joblib
- matplotlib
- seaborn


### Building Dependencies

````
conda env create -f environment.yml
pip install -r requirements
````


### Training the Model


### AWS

To serve the model locally, simply run
````
streamlit run PressorGauge.py
````

To create and run a Docker image locally, can call the script `local_build.sh`.

To publish a Docker image to [dockerhub](https://hub.docker.com) and push it to AWS, call the script `aws-docker-build/aws_build.sh`.
Note this file must be adapted for your local build.
The first line `source insight` activates the PressorGauge environment, changes directory to `PressorGauge`, and loads credentials as enviorenmental variables.


### Analysis

The data has been aggregated in 12-hour windows, with a 6-hr overlap between each window.
Those that end 12 hours or less from a pressor event define the positive class, everything else is negative.

Looking at the distribution between classes of some of the features shows correlation with pressor outcome.
For example, this is visible in the partial-pressure O2 (blood gas test):

![pO2 distributions](https://github.com/wrs28/PressorGauge/blob/master/images/pO2_dist.png)


A preliminary model training gives random forest feature importances, which can be compared to the Shapley importances (explained [here](https://github.com/slundberg/shap)), which show that among the lab features considered here, a long PTT (prothrombin time [test]), a high partial pressure O2, and an abnormal lactate test all strongly influence the classification.

![Shapley importances](https://github.com/wrs28/PressorGauge/blob/master/images/random_forest_shapley.png)

The model is trained on `11_777` test windows, and the learning curve suggests that the model does not suffer too much from overfitting.

![Random Forest Learning Curve](https://github.com/wrs28/PressorGauge/blob/master/images/random_forest_learning_curve.png)

The AUROC score of the model is .7, with mean time from prediction to event of 8 hours.

![Random Forest ROC curve](https://github.com/wrs28/PressorGauge/blob/master/images/random_forest_roc.png)
