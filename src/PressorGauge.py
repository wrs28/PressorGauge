import streamlit as st
import os
import numpy as np
import pandas as pd
import pickle
from modeling.feature_definitions import features_to_keep
import shap
import copy
import statistics
import altair as alt

# block for AWS SQL-access
# # DB_USER = os.environ.get("DB_USER")
# # DB_PASSWORD = os.environ.get("DB_PASSWORD")
# # DB_HOST = os.environ.get("DB_HOST")
# # DB_NAME = os.environ.get("DB_NAME")
# # engine = sqlalchemy.create_engine('postgres://postgres:postgres@host.docker.internal/PressorGauge')
# # engine = sqlalchemy.create_engine("postgres://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + "/" + DB_NAME)

#header
"""
# Pressor Gauge

### Predicting the need for life-saving blood-pressure medication (pressor) in the next 12 hours

-----
"""

with open(os.path.join("modeling","test_set.p"),"rb") as file:
    test_set = pickle.load(file)

agree = st.sidebar.checkbox('show ground truth?')

X, y, subjects = test_set["X"], test_set["y"], test_set["cv_groups"]

#ids = np.random.choice(subjects,size=10,replace=False)
ids = [23262,5199,89402,6558,10780,8992,17551,16646,21015,20083,24616,77484,99863,15659,91222,57764,9808,63987]

id_ind = st.sidebar.selectbox(
    'select a patient',
    range(len(ids))
)

st.sidebar.markdown("Patient Information & Labs:")

subject_id = ids[id_ind]
with open(os.path.join("modeling","test_set.p"),"rb") as file:
    test_set = pickle.load(file)

hadm_id = X[X.SUBJECT_ID==subject_id].HADM_ID.unique()[0];
inds = (X.SUBJECT_ID==subject_id) & (X.HADM_ID==hadm_id).values
y = y[inds]
X = X[inds]
X.pop("HADM_ID")
X.pop("SUBJECT_ID");
times = X.pop("EPOCH");
X.pop("PRESSOR_AT_ALL");
y[times > 2] = False

Q = X.copy()
Q = pd.DataFrame(Q.iloc[0,:]).T

# load up trained models
with open(os.path.join("modeling","random_forest_calibrated.p"),"rb") as file:
  model = pickle.load(file)

y_pred = model.predict(X)
p_pred = model.predict_proba(X)[:,1]

X["Probability of pressor need"] = p_pred
X["Hours since hospital admission"] = 6*times[::-1]
X["PRESSORS LIKELY"] = p_pred>.5
c1 = alt.Chart(X).mark_circle(size=100, color="gray").encode(
    x=alt.X('Hours since hospital admission:Q', scale=alt.Scale(domain=(6*times.values[0]-1,6*times.values[-1]+1))),
    y=alt.Y('Probability of pressor need:Q', scale=alt.Scale(domain=(-.1,1.1))),
)

if y_pred[0]:
    color="red"
else:
    color="steelblue"

c2 = alt.Chart(pd.DataFrame(X.iloc[0,:]).T).mark_circle(size=200, color=color, opacity=.7).encode(
    x=alt.X('Hours since hospital admission:Q', scale=alt.Scale(domain=(6*times.values[0]-1,6*times.values[-1]+1))),
    y=alt.Y('Probability of pressor need:Q', scale=alt.Scale(domain=(-.1,1.1))),
)

st.altair_chart(c1 + c2)

with open(os.path.join("modeling","random_forest_test_shapley_values.p"),"rb") as file:
    dict = pickle.load(file)
    explainer = dict["explainer"]
    shap_values = dict["shap_values"]

# following block repeats lab values in sidebar and enables them to be updated
if True:
    age = st.sidebar.number_input("age", value=Q["AGE"].values[0])
    Q["AGE"] = age

    if Q.GENDER.values[0]==1:
        sex_value = "F"
    else:
        sex_value = "M"
    sex = st.sidebar.radio("sex", ["M","F"], index=int(Q.GENDER.values[0]))
    if sex == "F":
        sex_value = 1
    else:
        sex_value = 0
    Q["GENDER"] = sex_value

    weight = st.sidebar.number_input("weight (kg)", value=Q["WEIGHT_KG"].values[0])
    Q["WEIGHT_KG"] = weight

    ptt = st.sidebar.number_input("PTT", value=Q["ptt_LAST"].values[0])
    Q["ptt_LAST"] = ptt

    po2 = st.sidebar.number_input("pO2", value=Q["pO2_LAST"].values[0])
    Q["pO2_LAST"] = po2

    lc = st.sidebar.checkbox("abnormal lactate?", value=Q["lactate_FLAG_COUNT"].values[0])
    Q["lactate_FLAG_COUNT"] = lc

    wbc = st.sidebar.checkbox("abnormal white blood cell count?", value=Q["wbc_FLAG_COUNT"].values[0])
    Q["wbc_FLAG_COUNT"] = wbc

    ph = st.sidebar.number_input("pH", value=Q["pH_LAST"].values[0])
    Q["pH_LAST"] = ph

    bun = st.sidebar.number_input("BUN", value=Q["bun_LAST"].values[0])
    Q["bun_LAST"] = bun

    cr = st.sidebar.number_input("Cr", value=Q["creatinine_LAST"].values[0])
    Q["creatinine_LAST"] = cr

    ag = st.sidebar.number_input("anion gap", value=Q["anion_gap_LAST"].values[0])
    Q["anion_gap_LAST"] = ag

    pco2 = st.sidebar.number_input("pCO2", value=Q["pCO2_LAST"].values[0])
    Q["pCO2_LAST"] = pco2

    pc = st.sidebar.number_input("platelet count", value=Q["platelet_count_LAST"].values[0])
    Q["platelet_count_LAST"] = pc

    hg = st.sidebar.number_input("hemoglobin", value=Q["hemoglobin_LAST"].values[0])
    Q["hemoglobin_LAST"] = hg

    hc = st.sidebar.number_input("hematocrit", value=Q["hematocrit_LAST"].values[0])
    Q["hematocrit_LAST"] = hc

    sodium = st.sidebar.number_input("Na+", value=Q["sodium_LAST"].values[0])
    Q["sodium_LAST"] = sodium

    chloride = st.sidebar.number_input("Cl-", value=Q["chloride_LAST"].values[0])
    Q["chloride_LAST"] = chloride

    pot = st.sidebar.number_input("K+", value=Q["potassium_LAST"].values[0])
    Q["potassium_LAST"] = pot

    bcb = st.sidebar.number_input("HCO3", value=Q["hcO3_LAST"].values[0])
    Q["hcO3_LAST"] = bcb

    alb = st.sidebar.checkbox("abnormal albumin?", value=Q["albumin_FLAG_COUNT"].values[0])
    Q["albumin_FLAG_COUNT"] = alb

    ap = st.sidebar.checkbox("abnormal alkaline phosphatase?", value=Q["alkaline_phosphatase_FLAG_COUNT"].values[0])
    Q["alkaline_phosphatase_FLAG_COUNT"] = ap

    ast = st.sidebar.checkbox("abnormal AST?", value=Q["AST_FLAG_COUNT"].values[0])
    Q["AST_FLAG_COUNT"] = ast

    ALT = st.sidebar.checkbox("abnormal ALT?", value=Q["ALT_FLAG_COUNT"].values[0])
    Q["ALT_FLAG_COUNT"] = ALT


new_pred = model.predict(Q)
new_prob = model.predict_proba(Q)[0,1]

f"""
Current probability of needing pressors in the next 12 hours: **{"%2i%%" % (100*new_prob)}**
"""

shap_values = explainer.shap_values(Q, approximate=False, check_additivity=False)

shapvals = shap_values[1][0,:]
a = np.argsort(shapvals)[::-1]
b = np.argsort(shapvals)
top_factors = Q.columns[a[0:3]]
bot_factors = Q.columns[b[0:3]]
tot_shap = sum(np.abs(shapvals))

x = Q.iloc[0,:]

# show top three influential lab results as markdown table
if new_pred:
    f"""
    Factors making pressors **likely** (ranked from most to least influential)

    |  | lab | result | importance (scale of 0-100) |
    |-  |-  |-  |
    | 1 | {top_factors[0]} | {x[a[0]]} | {"%2i" % (100*shapvals[a[0]]/tot_shap)}
    | 2 | {top_factors[1]} | {x[a[1]]} | {"%2i" % (100*shapvals[a[1]]/tot_shap)}
    | 3 | {top_factors[2]} | {x[a[2]]} | {"%2i" % (100*shapvals[a[2]]/tot_shap)}
    """
else:
    f"""
    Factors making pressors ** *un*likely** (ranked from most to least influential)

    |  | lab | result  | importance (scale of 0-100) |
    |-  |-  |-  |
    | 1 | {bot_factors[0]} | {x[b[0]]} | {"%2i" % (-100*shapvals[b[0]]/tot_shap)}
    | 2 | {bot_factors[1]} | {x[b[1]]} | {"%2i" % (-100*shapvals[b[1]]/tot_shap)}
    | 3 | {bot_factors[2]} | {x[b[2]]} | {"%2i" % (-100*shapvals[b[2]]/tot_shap)}

    """

"""
----
"""

# Show historical outcome vs predicted outcome
if agree:
    X["Predicted (purple)"] = y_pred
    X["Ground Truth (gray)"] = y
    c3 = alt.Chart(X).mark_circle(size=100, color="gray").encode(
        x=alt.X('Hours since hospital admission:Q', scale=alt.Scale(domain=(6*times.values[0]-1,6*times.values[-1]+1))),
        y=alt.Y('Ground Truth (gray):Q', scale=alt.Scale(domain=(-.1,1.1)), axis=alt.Axis(title="Classification (1 = pressor, 0 = none)")),
    )
    c4 = alt.Chart(X).mark_circle(size=50, color="#7D3C98").encode(
        x=alt.X('Hours since hospital admission:Q', scale=alt.Scale(domain=(6*times.values[0]-1,6*times.values[-1]+1))),
        y=alt.Y('Predicted (purple):Q', scale=alt.Scale(domain=(-.1,1.1))),
    ).interactive().properties(title="Pred. (purple) vs Truth (gray)")#, color=alt.Color('y',  scale=alt.Scale(scheme='blueorange')))

    c = c3 + c4

    c.configure_title(
        fontSize=30,
        font='Courier',
        anchor='start',
        color='gray',
    )

    c.configure_axis(
        labelFontSize=20
    )

    st.altair_chart(c)

    """
    -----
    """


# Footer
"""
Created by William R. Sweeney, Data Science Insight Fellow 2020

[github](https://github.com/wrs28/PressorGauge) |
[slides](https://docs.google.com/presentation/d/1O2QuISdaB0OOj7BF372qH_N30NvK4DMR628YFlL2-XE/edit?usp=sharing)
| [linkedin](https://www.linkedin.com/in/wrsweeney2/)
"""
