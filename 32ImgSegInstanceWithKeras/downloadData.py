# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 16:01:42 2019

@author: lewisliu
"""

import os
import zipfile

import matplotlib as mpl
mpl.rcParams['axes.grid'] = False
mpl.rcParams["figure.figsize"] = (12, 12)


import kaggle

#download data
competition_name = "carvana-image-masking-challenge"
competition_data_path = "/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/Studying/carvana-image-masking-challenge"
# Download data from Kaggle and unzip the files of interest.
def load_data_from_zip(competition, file):
    with zipfile.ZipFile(os.path.join(competition, file), "r") as zip_ref:
        unzipped_file = zip_ref.namelist()[0]
        zip_ref.extractall(competition)

def get_data(competition, competition_data_path):
    print("download begin..")
    kaggle.api.competition_download_files(competition, competition_data_path)
    print("download finished.")
#    load_data_from_zip(competition_data_path, "train.zip")
#    load_data_from_zip(competition_data_path, "train_masks.zip")
#    load_data_from_zip(competition_data_path, "train_masks.csv.zip")

get_data(competition_name, competition_data_path)