#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate PressorGauge

python ./src/build_pressor_database.py
python ./src/build_intervals.py
python ./src/build_chart_database.py
python ./src/build_lab_database.py
