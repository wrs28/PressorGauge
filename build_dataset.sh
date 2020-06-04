#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate insight

python ./src/build_data_set/chart_flagged_by_vent.py
python ./src/build_data_set/extract_timeline.py
python ./src/build_data_set/extract_relevant_chart_events.py
python ./src/build_data_set/extract_rest.py
