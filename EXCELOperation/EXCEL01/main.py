#!/usr/bin/python
#coding:utf-8
from pandas import DataFrame, read_csv
import pandas as pd
# import openpyxl
from logInfo import Logger
from tqdm import tqdm

# log = Logger('all.log', level='debug')
log = Logger('all.log', level='info')

file_path = 'data01_01_res.xlsx'
df = pd.read_excel(file_path)
# log.logger.info(df['企业名称'])
data = df.head()

data = df.ix[2].values

data = df.ix[1,8]
#*[1, 6]: 2, [1, 7]: 51, [1, 8]: 51, [1, 9]:102

print(data)
# if pd.isna(data):
#     print("1")
# else:
#     print("0")

class Company():
    def __init__(self):
        self.base_row = None
        self.name = None
        self.p_num = 0
        self.money_sum = 0


comp = Company()

row_begin = 1
row_end = 11913
for row in tqdm(range(row_begin,row_end+1)):
    if not pd.isna(df.ix[row, 1]):
        #* find new company
        #* update pre company
        if comp.base_row != None:
            df.ix[comp.base_row,6] = comp.p_num
            df.ix[comp.base_row,9] = comp.money_sum

        #* a new comanpy begin
        comp.base_row = row
        comp.name = df.ix[row, 1]
        comp.p_num = 1
        comp.money_sum = df.ix[row, 8]
    else:
        if not pd.isna(df.ix[row, 8]):
            comp.p_num += 1
            # comp.money_sum += df.ix[row, 8].astype(float)
            comp.money_sum += pd.to_numeric(df.ix[row, 8], errors='coerce')


#* write result
# df_write = pd.read_excel('data01_01_res.xlsx')
df.to_excel('data01_01_res_res.xlsx', index=False)
