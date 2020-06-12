import numpy as np


features = {

"lactate" : { # *
  "ab": "lc",
  "S" : "L",
  "V" : [50813],
  "min" : 0,
  "max" : 50
},

"pCO2" : {
  "ab": "pCO2",
  "S" : "L",
  "V" : [50818],
  "min" : 0,
  "max" : np.inf
},

"pH" : { # *
  "ab": "pH",
  "S" : "L",
  "V" : [50820],
  "min" : 6,
  "max" : 8
},

"pO2" : {
  "ab": "pO2",
  "S" : "L",
  "V" : [50821],
  "min" : 0,
  "max" : 800
},

"ALT" : {
  "ab": "alt",
  "S" : "L",
  "V" : [50861],
  "min" : 0,
  "max" : np.inf
},

"albumin" : {
  "ab" : "alb",
  "S" : "L",
  "V" : [50862],
  "min" : 0,
  "max" : 10
},

"alkaline phosphatase" : {
  "ab": "ap",
  "S" : "L",
  "V" : [50863],
  "min" : 0,
  "max" : np.inf
},

"anion gap" : {
  "ab": "ag",
  "S" : "L",
  "V" : [50868],
  "min" : 0,
  "max" : 10000
},

"AST" : {
  "ab": "ast",
  "S" : "L",
  "V" : [50878],
  "min" : 0,
  "max" : np.inf
},

"bicarbonate" : {
  "ab": "bcb",
  "S" : "L",
  "V" : [50882],
  "min" : 0,
  "max" : 10000
},

"bilirubin direct" : {
  "ab": "blrd",
  "S" : "L",
  "V" : [50883],
  "min": 0,
  "max": 150
},

"bilirubin total" : {
  "ab": "blrt",
  "S" : "L",
  "V" : [50885],
  "min": 0,
  "max": 150
},

"choride" : {
  "ab": "chl",
  "S" : "L",
  "V" : [50902],
  "min" : 0,
  "max" : 10000
},

"creatinine" : { # *
  "ab": "ct",
  "S" : "L",
  "V" : [50912],
  "min" : 0,
  "max" : 150
},

# "estimated GFR" : {
  # "ab": "gfr",
  # "S" : "L",
  # "V" : [50920]
# },

"lipase" : {
  "ab" : "lip",
  "S" : "L",
  "V" : [50956],
  "min" : 0,
  "max" : np.inf
},

"potassium" : {
  "ab" : "pot",
  "S" : "L",
  "V" : [50971],
  "min" : 0,
  "max" : 30
},

"sodium" : {
  "ab": "sod",
  "S" : "L",
  "V" : [50824, 50983],
  "min" : 0,
  "max" : 200
},

"tryponin I" : {
  "ab" : "trp",
  "S" : "L",
  "V" : [51002],
  "min" : 0,
  "max" : np.inf
},

"urea nitrogen" : {
  "ab": "un",
  "S" : "L",
  "V" : [51006],
  "min" : 0,
  "max" : 300
},

"hematocrit" : {
  "ab": "hmc",
  "S" : "L",
  "V" : [51221],
  "min" : 0,
  "max" : 100
},

"hemoglobin" : { # *
  "ab": "hg",
  "S" : "L",
  "V" : [50811,51222],
  "min" : 0,
  "max" : 150
},

"platelet count" : {
  "ab": "pc",
  "S" : "L",
  "V" : [51265],
  "min" : 0,
  "max" : 10000
},

"PTT" : {
  "ab": "ptt",
  "S" : "L",
  "V" : [51275],
  "min" : 0,
  "max" : 150
},

"wbc" : {
  "ab": "wbc",
  "S" : "L",
  "V" : [51301,51301],
  "min" : 0,
  "max" : 1000
},

"systolic blood pressure" : {
  "ab": "sbp",
  "S" : "C",
  "V" : [51,442,455,6701,220179,220050],
  "min" : 0,
  "max" : 400
},

"diastolic blood pressure" : {
  "ab": "dbp",
  "S" : "C",
  "V" : [8368,8440,8441,8555,220180,220051],
  "min" : 0,
  "max" : 300
},

"mean blood pressure" : {
  "ab": "mbp",
  "S" : "C",
  "V" : [456,52,6702,443,220052,220181,225312],
  "min" : 0,
  "max" : 400
},

"heart rate" : {
  "ab": "hr",
  "S" : "C",
  "V" : [211,220045],
  "min" : 0,
  "max" : 300
},

"respiratory rate" : {
  "ab": "rr",
  "S" : "C",
  "V" : [615,618,220210,224690],
  "min" : 0,
  "max" : 70
},

"glucose" : {
  "ab": "gc",
  "S" : "C",
  "V" : [807,811,1529,3745,3744,225664,220621,226537],
  "min" : 0,
  "max" : 10000
},

"spO2" : {
  "ab": "spO2",
  "S" : "C",
  "V" : [646, 220277],
  "min" : 0,
  "max" : 100
},


}




import numpy as np

def first(arr):
    return arr.iloc[0]


def last(arr):
    return arr.iloc[-1]


def add_features(data, feature_list, chart, lab):
    for feature in feature_list:
        cl = features[feature]["S"]
        if cl == "C":
            ident = "ICUSTAY_ID"
            chartlab = chart
        else:
            ident = "HADM_ID"
            chartlab = lab

        ab = features[feature]["ab"]

        group = chartlab.loc[chartlab.ITEMID.isin(features[feature]["V"])].groupby(ident)

        df_first = group.agg({"VALUENUM" : first, "CHARTTIME" : first})
        df_first.rename(columns={"VALUENUM" : ab + "_FIRST", "CHARTTIME" :  ab + "_FIRST_TIME"}, inplace=True)
        df_first.reset_index(inplace=True)

        df_last = group.agg({"VALUENUM" : last, "CHARTTIME" : last})
        df_last.rename(columns={"VALUENUM" : ab + "_LAST" , "CHARTTIME" :  ab + "_LAST_TIME"}, inplace=True)
        df_last.reset_index(inplace=True)

        df_mean = group.agg({"VALUENUM" : np.mean})
        df_mean.rename(columns={"VALUENUM" : ab + "_MEAN"}, inplace=True)
        df_mean.reset_index(inplace=True)

        df_std = group.agg({"VALUENUM" : np.std})
        df_std.rename(columns={"VALUENUM" : ab + "_STD"}, inplace=True)
        df_std.reset_index(inplace=True)

        df_min = group.agg({"VALUENUM" : np.min})
        df_min.rename(columns={"VALUENUM" : ab + "_MIN"}, inplace=True)
        df_min.reset_index(inplace=True)

        df_max = group.agg({"VALUENUM" : np.max})
        df_max.rename(columns={"VALUENUM" : ab + "_MAX"}, inplace=True)
        df_max.reset_index(inplace=True)

        data = data.join(df_first.set_index(ident), on=ident, how="left")
        data = data.join(df_last.set_index(ident) , on=ident, how="left")
        data = data.join(df_mean.set_index(ident) , on=ident, how="left")
        data = data.join(df_std.set_index(ident) , on=ident, how="left")
        data = data.join(df_min.set_index(ident) , on=ident, how="left")
        data = data.join(df_max.set_index(ident) , on=ident, how="left")
        data[ab + "_RATE"] = 60*(data[ab + "_LAST"] - data[ab + "_FIRST"])/((data[ab + "_LAST_TIME"] - data[ab + "_FIRST_TIME"]))

    # df_mid = group.agg({"WINDOW_MID" : first})
    # df_mid.reset_index(inplace=True)
    # data = data.join(df_mid.set_index(ident) , on=ident, how="left")


    return data
