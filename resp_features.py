features = {
  "respiratory rate" : {
    "ab": "RR",
    "C" : [224422,224689] + [220210, 224690], # spont + total
    "L" : []
  },
  "tidal volume" : {
    "ab": "TV",
    "C" : [224421, 224686] + [224685, 2408], # spont + observed
    "L" : []
  },
  "minute volume" : {
    "ab": "MV",
    "C" : [445, 448, 449, 450, 1340, 1486, 1600, 22468],
    "L" : []
  },
  "blood pH" : {
    "ab": "ph",
    "C" : [], #[223830, 227543, 220734],
    "L" : [50820]
  },
  "non invasive blood pressure diastolic" : {
    "ab": "nibp_d",
    "C" : [220180, 227242, 224643],
    "L" : []
  },
  "non invasive blood pressure systolic" : {
    "ab" : "nibp_s",
    "C" : [224167, 227243, 220179],
    "L" : []
  },
  "spO2" : {
    "ab": "spO2",
    "C" : [220277],
    "L" : []
  },
  "svO2" : {
    "ab": "svO2",
    "C" : [223772],
    "L" : []
  },
  "FiO2" : {
    "ab": "FiO2",
    "C" : [223835],
    "L" : []
  },
  "heart rate" : {
    "ab": "hr",
    "C" : [220045],
    "L" : []
  },
  "O2 flow" : {
    "ab": "O2f",
    "C" : [223834],
    "L" : []
  },
  "resistance" : {
    "ab" : "res",
    "C" : [220283],
    "L" : [],
  },
  "apnea interval" : {
    "ab": "apin",
    "C" : [223876],
    "L" : []
  },
  "CO2 production" : {
    "ab": "CO2p",
    "C" : [220245],
    "L" : []
  },
  "respiratory quotient" : {
    "ab": "rq",
    "C" : [224745],
    "L" : []
  },
  "PEEP" : {
    "ab": "peep",
    "C" : [224700],
    "L" : []
  },
  "peak insp. pressure" : {
    "ab": "pip",
    "C" : [224695],
    "L" : []
  },
  "plateau pressure" : {
    "ab": "pp",
    "C" : [224696],
    "L" : []
  },
  "negative inspiration force" : {
    "ab": "nif",
    "C" : [224419],
    "L" : []
  },
  "arterial blood pressure" : {
    "ab": "abp",
    "C" : [225309,224697],
    "L" : []
  },
  "pO2" : {
    "ab": "pO2",
    "C" : [],
    "L" : [50821]
  },
  "pCO2" : {
    "ab": "pCO2",
    "C" : [],
    "L" : [50818],
  },
  "base excess" : {
    "ab": "be",
    "C" : [],
    "L" : [50802]
  },
  "O2 saturation" : {
    "ab" : "O2s",
    "C" : [],
    "L" : [50817],
  },
  "anion gap" : {
    "ab" : "ag",
    "C" : [],
    "L" : [50868]
  },
  "carboxyhemoglobin" : {
    "ab" : "ch",
    "C" : [],
    "L" : [50805]
  },
  "calculated total CO2" : {
    "ab" : "ctCO2",
    "C" : [],
    "L" : [50804]
  },
  "d-dimer" : {
    "ab" : "ddimer",
    "C" : [],
    "L" : [51196]
  }
}




import numpy as np

def last(arr):
    return arr.iloc[-1]


def add_chart_feature_agg(data, feature, chart, name_mod, aggregator):
    dff = chart.loc[chart["ITEMID"].isin(features[feature]["C"])].groupby("ICUSTAY_ID").agg({"VALUENUM" : aggregator})
    dff.rename(columns={"VALUENUM" : features[feature]["ab"] + "_" + name_mod}, inplace=True)
    dff.reset_index(inplace=True)
    return data.join(dff.set_index("ICUSTAY_ID"),on="ICUSTAY_ID",how="left")


def add_lab_feature_agg(data, feature, lab, name_mod, aggregator):
    dff = lab.loc[lab["ITEMID"].isin(features[feature]["L"])].groupby("SUBJECT_ID").agg({"VALUENUM" : aggregator})
    dff.rename(columns={"VALUENUM" : features[feature]["ab"] + "_" + name_mod}, inplace=True)
    dff.reset_index(inplace=True)
    return data.join(dff.set_index("SUBJECT_ID"),on="SUBJECT_ID",how="left")


def add_feature(data, feature, charts, labs, num_mod):
    if len(features[feature]["C"]) > 0:
      data = add_chart_feature_agg(data, feature, charts, "MEAN" + str(num_mod), np.mean)
      data = add_chart_feature_agg(data, feature, charts, "MAX"  + str(num_mod), np.max)
      data = add_chart_feature_agg(data, feature, charts, "MIN"  + str(num_mod), np.min)
      data = add_chart_feature_agg(data, feature, charts, "LAST" + str(num_mod), last)
    if len(features[feature]["L"]) > 0:
      data = add_lab_feature_agg(data, feature, labs, "MEAN" + str(num_mod), np.mean)
      data = add_lab_feature_agg(data, feature, labs, "MAX"  + str(num_mod), np.max)
      data = add_lab_feature_agg(data, feature, labs, "MIN"  + str(num_mod), np.min)
      data = add_lab_feature_agg(data, feature, labs, "LAST" + str(num_mod), last)
    return data

def add_difference(data, feature, measure):
    ab = features[feature]["ab"]
    data[ab + "_DIFF"] = data[ab + "_" + measure + "2"] - data[ab + "_" + measure + "1"]
    return data
