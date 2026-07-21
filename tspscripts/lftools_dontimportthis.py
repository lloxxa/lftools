import numpy as np, matplotlib.pyplot as pp
import autotools as at
import sys

def openALV(filename, find=["\"Correlation\"","\"Count Rate\""]):
	found={i:[] for i in find}
	print("Gonna look for "+str(find))

	data=[[]]
	with open(filename) as f:
		for line in f:
			data.append(line.split())
	#print data
	for i in find: #can also be done without a loop, but this is easier to read
		indexi=data.index(i.split())
		indexj=indexi+data[indexi:].index([])
		print(str(indexi), str(indexj))
		found[i]=np.array(data[indexi+1:indexj],float)
		#found=False
		#while tofind[i]:
		#for line in data:
	
	return found

# TODO: write an object that stores the relevant info for a correlation curve
# 	such as temperature, as the current procedure looses track of the file's identity
#	and only stores the decontextualized data
def openseries(path="",mask="*"):
	series=at.Data(path,mask)
	datas=[openALV(i) for i in series.get_filelist()]
	correlations=[i[ "\"Correlation\"" ] for i in datas]
	counts=[i[ "\"Count Rate\"" ] for i in datas]
	return correlations, counts

def open_mc(filename, nc=2):
	data=[[]]
	with open(filename) as f:
		cnt=1
		for line in f:
			words=line.split()
			if len(words)!=mc:
				print("Skipping line n=%i"%(cnt))
			if len(words)==mc:
				data.append([float(i) for i in words])
			cnt+=1
	data=np.array(data[1:len(data)])
	return(data)

# def main(*args):
#	if len(args) not 3:
#		print("Usage: rea")
#		sys.exit()
#	with open(args[1]) as f:
		
