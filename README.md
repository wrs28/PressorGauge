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


###


### Analysis


![Random Forest ROC curve](https://github.com/wrs28/PressorGauge/blob/master/images/random_forest_roc.png)
