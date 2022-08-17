#!/user/bin/env python3
#-*-　encoding:utf-8　-*-
'''
Created on Wed March 17 19:04:56 2021

@Author: LewisLiu
@Description:
'''
from pandas import DataFrame, read_csv
import pandas as pd
# import openpyxl
from logInfo import Logger
from tqdm import tqdm

# log = Logger('all.log', level='debug')
log = Logger('all.log', level='info')

file_path = 'data_01.xlsx'
df = pd.read_excel(file_path)
# log.logger.info(df['企业名称'])
data = df.head()

data = df.values[0]
print(data)
data = df.values[0,0]
print(data)
if pd.isna(data):
    print("1")
else:
    print("0")

data_res = {"A":[], "B":[], "C":[], "D":[]}


class Major():
    def __init__(self):
        self.level_1 = None
        self.level_2 = None
        self.level_3 = None
        self.level_4 = []
    
    def is_valid(self):
        if self.level_1 != None and self.level_2 != None and self.level_3 != None and len(self.level_4) > 0:
            return True
        return False


major = Major()

def check_valid_row(row_values):
    if len(row_values) != 4:
        return False
    
    if not pd.isna(row_values[0]):
        if pd.isna(row_values[1]) or pd.isna(row_values[2]) or pd.isna(row_values[3]):
            return False
    
    if not pd.isna(row_values[1]):
        if pd.isna(row_values[2]) or pd.isna(row_values[3]):
            return False
    
    if not pd.isna(row_values[2]) and pd.isna(row_values[3]):
        return False

    return True

def add_major_2_res_row(major, cur_row):
    data_res["A"].append("{}".format(major.level_1))
    data_res["B"].append("{}".format(major.level_2))
    data_res["C"].append("{}".format(major.level_3))
    cur_level_4 = ""
    for index in range(len(major.level_4)):
        if index == 0:
            cur_level_4 = "{}".format(major.level_4[0])
        else:
            cur_level_4 = "{};{}".format(cur_level_4, major.level_4[index])
    data_res["D"].append(cur_level_4)

row_begin = 0
row_end = 3909
cur_res_row = 0
for row in tqdm(range(row_begin,row_end)):
    is_valid = check_valid_row(df.values[row])
    if not is_valid:
        print("{}'s value is invalid!".format(row))

    if not pd.isna(df.values[row, 2]):
        if major.is_valid():
            add_major_2_res_row(major, cur_res_row)
        else:
            print("major is invalid!")

        #* update major
        major.level_3 = df.values[row, 2]
        if not pd.isna(df.values[row, 1]): major.level_2 = df.values[row, 1]
        if not pd.isna(df.values[row, 0]): major.level_1 = df.values[row, 0]
        major.level_4 = []
    
    major.level_4.append(df.values[row, 3])

if major.is_valid():
    add_major_2_res_row(major, cur_res_row)


# #* write result
# # df_write = pd.read_excel('data01_01_res.xlsx')
df_res = pd.DataFrame(data_res)
print(df_res.values[-2])
print(df_res.values[-1])
df_res.to_excel('data01_01.xlsx', index=False)
