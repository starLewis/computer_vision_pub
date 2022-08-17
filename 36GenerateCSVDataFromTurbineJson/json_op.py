#!/user/bin/env python3
# -*- encoding: utf-8 -*-
'''
Created on Wed March 17 18:02:12 2021

@Author: LewisLiu
@Description:
'''
import json
import os
import sys

def file_2_json(file_path):
    json_data = None
    with open(file_path, "r") as fp:
        json_data = json.load(fp)

    fp.close()

    return json_data

def json_2_file(json_data, file_path):
    with open(file_path, "w") as outfile:
        json.dump(json_data, outfile)

    outfile.close()