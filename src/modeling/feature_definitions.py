import numpy as np
import pandas as pd
# from features_dict import features
# from modeling.features_dict import features
# from src.modeling.features_dict import features


features_to_keep = [

    # # "LODS",
    #
    # # "OASIS",
    #
    # # "APACHE",
    #
    # # "CARDIOVASCULAR_LODS",
    #
    # # "PULMONARY_LODS",
    #
    "AGE",
    #
    "TOTAL_FLAG_COUNT",
    #
    "GENDER", # really sex
    #
    "WEIGHT_KG",
    #
    # # "lc_MIN",
    # # "lc_MAX",
    # # "lc_MEAN",
    "lactate_FLAG_COUNT",
    #
    # "pCO2_MIN",
    # "pCO2_MAX",
    "pCO2_LAST",
    # # "pCO2_MEAN",
    # "pCO2_FLAG_COUNT",
    # "pCO2_RHO",
    #
    # "pH_MIN",
    "pH_LAST",
    # "pH_MAX",
    # # "pH_MEAN",
    # "pH_FLAG_COUNT",
    # "pH_RHO",
    #
    # "pO2_MIN",
    # "pO2_MAX",
    "pO2_LAST",
    # # "pO2_MEAN",
    # "pO2_FLAG_COUNT",
    # "pO2_RHO",
    #
    # # "pO2_MIN",
    # # "gc_MAX",
    # # "pO2_MEAN",
    # "glucose_FLAG_COUNT",
    # "lipase_FLAG_COUNT",
    # "troponin_FLAG_COUNT",
    # "bilirubin_direct_FLAG_COUNT",
    # "bilirubin_total_FLAG_COUNT",
    #
    # # "alt_MIN",
    # # "alt_MAX",
    # # "alt_MEAN",
    "ALT_FLAG_COUNT",
    #
    # # "ast_MIN",
    # # "ast_MAX",
    # # "ast_MEAN",
    "AST_FLAG_COUNT",
    #
    # # "alb_MIN",
    # # "alb_MAX",
    # # "alb_MEAN",
    "albumin_FLAG_COUNT",
    #
    # # "ap_MIN",
    # # "ap_MAX",
    # # "ap_MEAN",
    "alkaline_phosphatase_FLAG_COUNT",
    #
    # # "ag_MIN",
    # "ag_MAX",
    "anion_gap_LAST",
    # # "ag_MEAN",
    # "ag_FLAG_COUNT",
    # "ag_RHO",
    #
    # "ct_MIN",
    # "ct_MAX",
    "creatinine_LAST",
    # # "ct_MEAN",
    # "ct_FLAG_COUNT",
    # "ct_RHO",
    #
    "chloride_LAST",
    # # "chl_MAX",
    # "cl_MEAN",
    # "cl_FLAG_COUNT",
    # "cl_RHO",
    #
    "sodium_LAST",
    # # "sod_MAX",
    # # "sod_MEAN",
    # "na_FLAG_COUNT",
    # "na_RHO",
    #
    "potassium_LAST",
    # # "pot_MAX",
    # # "pot_MEAN",
    # "k_FLAG_COUNT",
    # "k_RHO",
    #
    # "pc_MIN",
    "platelet_count_LAST",
    # # "pc_MAX",
    # # "pc_MEAN",
    # "pc_FLAG_COUNT",
    # "pc_RHO",
    #
    # # "un_MIN",
    # "bun_MAX",
    "bun_LAST",
    # # "un_MEAN",
    # "bun_FLAG_COUNT",
    # "bun_RHO",
    #
    # # "bcb_MIN",
    # "hcO3_MAX",
    "hcO3_LAST",
    # "hcO3_FLAG_COUNT",
    # "hcO3_RHO",
    #
    # # "pt_MIN",
    # # "pt_MAX",
    # # "pt_MEAN",
    # "pt_FLAG_COUNT",
    #
    # # "inrpt_MIN",
    # # "inrpt_MAX",
    # # "inrpt_MEAN",
    # "inrpt_FLAG_COUNT",
    #
    # # "ptt_MIN",
    # "ptt_MAX",
    "ptt_LAST",
    # # "ptt_MEAN",
    # "ptt_FLAG_COUNT",
    # "ptt_RHO",
    #
    # "wbc_MIN",
    # "wbc_MAX",
    # # "wbc_MEAN",
    "wbc_FLAG_COUNT",
    # "wbc_RHO",
    #
    # "hg_MIN",
    "hemoglobin_LAST",
    # # "hg_MAX",
    # # "hg_MEAN",
    # "hg_FLAG_COUNT",
    # "hg_RHO",
    #
    # "hmc_MIN",
    "hematocrit_LAST",
    # # "hmc_MAX",
    # "hmc_MEAN",
    # "hmc_FLAG_COUNT",
]


def find_first(row):
  arr = row.values
  idx = arr.argmax()
  if arr[idx]:
    return idx
  else:
    return None#len(arr) - 1


def find_last(row):
  arr = row.values
  return find_first(pd.Series(arr[::-1]))


def first(arr):
    return find_first(~arr.isna())


def last(arr):
    return arr.iloc[-1]#find_last(~arr.isna())


def attach_lab_features(data, lab):

    group = lab.groupby("HADM_ID")

    df_tot_flag_count = (group.FLAG.value_counts()/group.HADM_ID.size()).unstack().fillna(0).abnormal
    df_tot_flag_count.name = "TOTAL_FLAG_COUNT"

    df_tot_flag_count = df_tot_flag_count.reset_index()
    # df_tot_flag_count.rename({"FLAG": "TOTAL_FLAG_COUNT"}, inplace=True, axis=1)
    data = data.join(df_tot_flag_count.set_index("HADM_ID"), on="HADM_ID", how="left")

    df_last_time = group.HOURS_BEFORE_PRESSOR.min()
    df_last_time = df_last_time.reset_index()
    df_last_time.rename({"HOURS_BEFORE_PRESSOR": "LAST_LAB_TIME"}, inplace=True, axis=1)
    data = data.join(df_last_time.set_index("HADM_ID"), on="HADM_ID", how="left")

    # df_pressor_at_all = group.PRESSOR_AT_ALL.any()
    # df_pressor_at_all = df_pressor_at_all.reset_index()
    # data = data.join(df_pressor_at_all.set_index("HADM_ID"), on="HADM_ID", how="left")

    for feature in features:

        ident = "HADM_ID"
        chartlab = lab

        ab = features[feature]["ab"]

        group = chartlab.groupby(ident)
        if len(group)>0:
            df_flag_count = (group.FLAG.value_counts()).unstack().fillna(0).abnormal
            df_flag_count.name = "FLAG"
            df_flag_count = (df_flag_count>0).astype(int)
            df_flag_count = df_flag_count.reset_index()
            df_flag_count.rename({"FLAG": ab + "_FLAG_COUNT"}, inplace=True, axis=1)

        group = chartlab.loc[chartlab.ITEMID.isin(features[feature]["V"])].groupby(ident)

        if len(group)>0:
            # df_flag_count = (group.FLAG.value_counts()/group.size()).unstack().fillna(0).abnormal
            df_flag_count = (group.FLAG.value_counts()).unstack().fillna(0).abnormal
            df_flag_count.name = "FLAG"
            df_flag_count = (df_flag_count>0).astype(int)
            df_flag_count = df_flag_count.reset_index()
            df_flag_count.rename({"FLAG": ab + "_FLAG_COUNT"}, inplace=True, axis=1)

            # df_flag_count = pd.DataFrame{}

            # df_first = group.agg({"VALUENUM" : first, "CHARTTIME" : first})
            # df_first.rename(columns={"VALUENUM" : ab + "_FIRST", "CHARTTIME" :  ab + "_FIRST_TIME"}, inplace=True)
            # df_first.reset_index(inplace=True)

            df_last = group.agg({"VALUENUM" : last})#, "CHARTTIME" : last})
            # df_last.rename(columns={"VALUENUM" : ab + "_LAST" , "CHARTTIME" :  ab + "_LAST_TIME"}, inplace=True)
            df_last.rename(columns={"VALUENUM" : ab + "_LAST"}, inplace=True)
            df_last.reset_index(inplace=True)

            df_mean = group.agg({"VALUENUM" : np.mean})
            df_mean.rename(columns={"VALUENUM" : ab + "_MEAN"}, inplace=True)
            df_mean.reset_index(inplace=True)

            # df_std = group.agg({"VALUENUM" : np.std})
            # df_std.rename(columns={"VALUENUM" : ab + "_STD"}, inplace=True)
            # df_std.reset_index(inplace=True)

            df_min = group.agg({"VALUENUM" : np.min})
            df_min.rename(columns={"VALUENUM" : ab + "_MIN"}, inplace=True)
            df_min.reset_index(inplace=True)

            df_max = group.agg({"VALUENUM" : np.max})
            df_max.rename(columns={"VALUENUM" : ab + "_MAX"}, inplace=True)
            df_max.reset_index(inplace=True)

            # df_first = group.agg({"VALUENUM" : first})
            # df_last = group.agg({"VALUENUM" : last})
            # df_rho = df_first-df_last
            # df_rho.rename(columns={"VALUENUM" : ab + "_RHO"}, inplace=True)
            # df_rho.reset_index(inplace=True)

            data = data.join(df_flag_count.set_index(ident), on=ident, how="left")
            data = data.join(df_last.set_index(ident), on=ident, how="left")
            data = data.join(df_mean.set_index(ident) , on=ident, how="left")
            # data = data.join(df_std.set_index(ident) , on=ident, how="left")
            data = data.join(df_min.set_index(ident) , on=ident, how="left")
            data = data.join(df_max.set_index(ident) , on=ident, how="left")
            # data = data.join(df_rho.set_index(ident) , on=ident, how="left")
            # data[ab + "_RATE"] = 60*(data[ab + "_LAST"] - data[ab + "_FIRST"])/((data[ab + "_LAST_TIME"] - data[ab + "_FIRST_TIME"]))

    return data


def clean_data(data):
    data = data.copy()
    data.loc[data.WEIGHT_KG<25, "WEIGHT_KG"] = np.nan
    for key in features:
        feature = features[key]
        ab = feature["ab"]
        for suffix in ["MIN","MAX","MEAN","LAST"]: #,"RHO","STD","RATE"]:
            col_name = ab + "_" + suffix
            data.loc[data[ab + "_MIN"] <= feature["min"],col_name] = np.nan
            data.loc[data[ab + "_MAX"] >= feature["max"],col_name] = np.nan
            # data.loc[data[ab + "_RHO"] >= 1000, col_name] = np.nan
            # clean_data.loc[clean_data[ab + "_RATE"] == np.inf,col_name] = np.nan
            # clean_data.loc[clean_data[ab + "_RATE"] == -np.inf,col_name] = np.nan

    return data





features = {

"lactate" : {
  "ab": "lactate",
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
  "ab": "ALT",
  "S" : "L",
  "V" : [50861],
  "min" : 0,
  "max" : np.inf
},

"albumin" : {
  "ab" : "albumin",
  "S" : "L",
  "V" : [50862],
  "min" : 0,
  "max" : 10
},

"alkaline phosphatase" : {
  "ab": "alkaline_phosphatase",
  "S" : "L",
  "V" : [50863],
  "min" : 0,
  "max" : np.inf
},

"anion gap" : {
  "ab": "anion_gap",
  "S" : "L",
  "V" : [50868],
  "min" : 0,
  "max" : 10000
},

"AST" : {
  "ab": "AST",
  "S" : "L",
  "V" : [50878],
  "min" : 0,
  "max" : np.inf
},

"bicarbonate" : {
  "ab": "hcO3",
  "S" : "L",
  "V" : [50882],
  "min" : 0,
  "max" : 10000
},

"bilirubin direct" : {
  "ab": "bilirubin_direct",
  "S" : "L",
  "V" : [50883],
  "min": 0,
  "max": 150
},

"bilirubin total" : {
  "ab": "bilirubin_total",
  "S" : "L",
  "V" : [50885],
  "min": 0,
  "max": 150
},

"chloride" : {
  "ab": "chloride",
  "S" : "L",
  "V" : [50902],
  "min" : 0,
  "max" : 10000
},

"creatinine" : { # *
  "ab": "creatinine",
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
  "ab" : "lipase",
  "S" : "L",
  "V" : [50956],
  "min" : 0,
  "max" : np.inf
},

"glucose" : {
    "ab" : "glucose",
    "S" : "L",
    "V" : [50931],
    "min" : 0,
    "max" : np.inf
},

"potassium" : {
  "ab" : "potassium",
  "S" : "L",
  "V" : [50971],
  "min" : 0,
  "max" : 30
},

"sodium" : {
  "ab": "sodium",
  "S" : "L",
  "V" : [50824, 50983],
  "min" : 0,
  "max" : 200
},

"troponin I" : {
  "ab" : "troponin",
  "S" : "L",
  "V" : [51002],
  "min" : 0,
  "max" : np.inf
},

"urea nitrogen" : {
  "ab": "bun",
  "S" : "L",
  "V" : [51006],
  "min" : 0,
  "max" : 300
},

"INR PT" : {
  "ab" : "inrpt",
  "S" : "L",
  "V" : [51237],
  "min" : 0,
  "max" : np.inf
},

"PT" : {
  "ab" : "pt",
  "S" : "L",
  "V" : [51274],
  "min" : 0,
  "max" : np.inf
},

"hematocrit" : {
  "ab": "hematocrit",
  "S" : "L",
  "V" : [51221],
  "min" : 0,
  "max" : 100
},

"hemoglobin" : { # *
  "ab": "hemoglobin",
  "S" : "L",
  "V" : [50811,51222],
  "min" : 0,
  "max" : 150
},

"platelet count" : {
  "ab": "platelet_count",
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
  "V" : [51300,51301],
  "min" : 0,
  "max" : 1000
},

# "systolic blood pressure" : {
#   "ab": "sbp",
#   "S" : "C",
#   "V" : [51,442,455,6701,220179,220050],
#   "min" : 0,
#   "max" : 400
# },
#
# "diastolic blood pressure" : {
#   "ab": "dbp",
#   "S" : "C",
#   "V" : [8368,8440,8441,8555,220180,220051],
#   "min" : 0,
#   "max" : 300
# },
#
# "mean blood pressure" : {
#   "ab": "mbp",
#   "S" : "C",
#   "V" : [456,52,6702,443,220052,220181,225312],
#   "min" : 0,
#   "max" : 400
# },
#
# "heart rate" : {
#   "ab": "hr",
#   "S" : "C",
#   "V" : [211,220045],
#   "min" : 0,
#   "max" : 300
# },
#
# "respiratory rate" : {
#   "ab": "rr",
#   "S" : "C",
#   "V" : [615,618,220210,224690],
#   "min" : 0,
#   "max" : 70
# },
#
# "glucose" : {
#   "ab": "gc",
#   "S" : "L",
#   "V" : [50931],
#   "min" : 0,
#   "max" : 10000
# },
#
# "spO2" : {
#   "ab": "spO2",
#   "S" : "C",
#   "V" : [646, 220277],
#   "min" : 0,
#   "max" : 100
# },

}
