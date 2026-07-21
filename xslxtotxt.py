#!/usr/bin/python
import xlrd
import csv
import glob

for f in glob.glob("*.xlsx"):
	with open('f', 'wb') as csvfile:
		wr = csv.writer(csvfile, delimiter="\t")
		xslxfile = xlrd.open_workbook(f)
		mysheet = xlsxfile.sheet_by_index(0)
		for rownum in xrange(mysheet.nrows):	
	        	wr.writerow(mysheet.row_values(rownum))
