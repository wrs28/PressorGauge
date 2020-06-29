#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate PressorGauge

python ./src/modeling/split_data.py
python ./src/modeling/build_features.py
python ./src/modeling/preprocess_data.py
python ./src/modeling/train_random_forest.py
python ./src/modeling/test_random_forest.py
