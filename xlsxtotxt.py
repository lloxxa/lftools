#!/anaconda/bin/python
import xlrd
import csv
import glob
import rheotools as rt

for f in glob.glob("*.xlsx"):
	with open(rt.cleanfname(f[:-5]+'.txt'), 'wb') as csvfile:
		wr = csv.writer(csvfile, delimiter="\t")
		xlsxfile = xlrd.open_workbook(f)
		mysheet = xlsxfile.sheet_by_index(0)
		for rownum in xrange(mysheet.nrows):	
	        	wr.writerow([rt.cleanstr(unicode(s).encode('ascii','ignore')) for s in mysheet.row_values(rownum)])
