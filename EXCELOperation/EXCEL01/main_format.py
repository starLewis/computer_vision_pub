#!/usr/bin/python
#coding:utf-8
from pandas import DataFrame, read_csv
import pandas as pd
# import openpyxl
from logInfo import Logger
from tqdm import tqdm
import xlrd
import xlutils.copy

# log = Logger('all.log', level='debug')
log = Logger('all.log', level='info')

file_path = 'data01_01.xls'
df = pd.read_excel(file_path)

#rb打开该excel，formatting_info=True表示打开excel时并保存原有的格式
rb = xlrd.open_workbook(file_path,formatting_info=True)
#创建一个可写入的副本
wb = xlutils.copy.copy(rb)


data = df.ix[254,8]
#*[1, 6]: 2, [1, 7]: 51, [1, 8]: 51, [1, 9]:102

print(data)

num = pd.to_numeric(data, errors='coerce')
print(num)

def setOutCell(outSheet, col, row, value):
    """ Change cell value without changing formatting. """
    def _getOutCell(outSheet, colIndex, rowIndex):
        """ HACK: Extract the internal xlwt cell representation. """
        row = outSheet._Worksheet__rows.get(rowIndex)
        if not row: return None

        cell = row._Row__cells.get(colIndex)
        return cell

    # HACK to retain cell style.
    previousCell = _getOutCell(outSheet, col, row)
    # END HACK, PART I

    outSheet.write(row, col, value)

    # HACK, PART II
    if previousCell:
        newCell = _getOutCell(outSheet, col, row)
        if newCell:
            newCell.xf_idx = previousCell.xf_idx

class Company():
    def __init__(self):
        self.base_row = None
        self.name = None
        self.p_num = 0
        self.money_sum = 0
        self.cur_p_name = None


comp = Company()


SUM = 0
SUM_NA = 0
row_begin = 1
row_end = 11913
for row in tqdm(range(row_begin,row_end+2)):
    if not pd.isna(df.ix[row, 1]) or row == row_end+1:
        #* find new company
        #* update pre company
        if comp.base_row != None:
            df.ix[comp.base_row, 6] = comp.p_num
            df.ix[comp.base_row, 9] = comp.money_sum
            outSheet = wb.get_sheet(0)
            setOutCell(outSheet, 6, comp.base_row+1, comp.p_num)
            setOutCell(outSheet, 9, comp.base_row+1, comp.money_sum)
            # outSheet.write(comp.base_row+1, 6, comp.p_num)
            # outSheet.write(comp.base_row+1, 9, comp.money_sum)
            # print("write: {}, {}, {}".format(comp.base_row, 6, comp.p_num))

        #* a new comanpy begin
        comp.base_row = row
        comp.name = df.ix[row, 1]
        comp.p_num = 1
        comp.money_sum = df.ix[row, 8]
        comp.cur_p_name = df.ix[row,2]
    else:
        money = pd.to_numeric(df.ix[row, 8], errors='coerce')
        if not pd.isna(df.ix[row, 8]) and not pd.isna(money):
            # comp.money_sum += df.ix[row, 8].astype(float)
            comp.money_sum += pd.to_numeric(df.ix[row, 8], errors='coerce')
            SUM += pd.to_numeric(df.ix[row, 8], errors='coerce')
        if not pd.isna(df.ix[row, 2]) and df.ix[row, 2] != comp.cur_p_name:
            comp.p_num += 1
        else:
            SUM_NA += 1
        comp.cur_p_name = df.ix[row,2]


#* write result
# df_write = pd.read_excel('data01_01_res.xlsx')
# df.to_excel('data01_01_res_res_res.xlsx', index=False)
wb.save('output.xls')
print("SUM: {}".format(SUM))
print("SUM_NA: {}".format(SUM_NA))