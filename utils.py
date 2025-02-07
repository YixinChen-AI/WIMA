import pandas as pd
import json
import SimpleITK as sitk
fdg_df = pd.read_csv("/share/home/yxchen/dataset/autopet2024/fdg_metadata.csv")
psma_df = pd.read_csv("/share/home/yxchen/dataset/autopet2024/psma_metadata.csv")

def check_info(name):
    tmp = fdg_df[fdg_df["Unnamed: 22"] == "PETCT_"+name.split("_")[1]]
    assert len(tmp) != 0, "no data related to this name"
    tmp = tmp.iloc[0]
    return {
        "subject ID":tmp["Subject ID"],
        "diagnosis":tmp["diagnosis"],
        "age":tmp["age"],
        "sex":tmp["sex"]
    }
def check_split(name):
    with open("/share/home/yxchen/dataset/autopet2024/splits_final_fairness.json","r") as f:
        split = json.load(f)
    if name in split[0]["train"]:
        return "train"
    if name in split[0]["val"]:
        return "val"

