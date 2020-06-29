#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate PressorGauge

python ./src/building_database/build_pressor_database.py
python ./src/building_database/build_intervals.py
python ./src/building_database/build_lab_database.py
