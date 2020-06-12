import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import time
import sqlalchemy

import os



"""
# This is my first test
"""

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")


"""
or is it not again?
"""

"""
or is it? or is it not?
"""

"""
or maybe it still is
"""
#
# # engine = sqlalchemy.create_engine('postgres://postgres:postgres@host.docker.internal/PressorGauge')
engine = sqlalchemy.create_engine("postgres://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME)
#
icustay_id = st.text_input("",value="209989")
#
QUERY = f"""
select "ICUSTAY_ID", "HADM_ID"
from pressors_by_icustay
where "ICUSTAY_ID"={icustay_id}
"""
#
with engine.connect() as connection:
  vaso_episodes = pd.read_sql_query(QUERY, con=connection)
# #
vaso_episodes
