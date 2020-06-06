#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate insight

python ./src/build_data_set_resp/build_durations.py
# python ./src/build_data_set_resp/build_extras.py
# python ./src/build_data_set_resp/extract_relevant_chart_events.py
# # python ./src/build_data_set_resp/extract_relevant_lab_events.py
# python ./src/build_data_set_resp/extract_rest.py
