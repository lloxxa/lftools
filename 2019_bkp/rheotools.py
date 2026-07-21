import os, errno
import numpy as np
import string

obs=['Meas. Pts.','Time','Torque', 'Temperature', 'Shear Rate', 'Angular Frequency', 'Storage Modulus',
 'Loss Modulus', 'Viscosity']
dsi_constants=['Name', 'Sample', 'Operator', 'Number of Intervals', 'Application',
 'Device', 'Measuring Date/Time', 'Measuring System', 'Accessories',
 '- Csr [min/s]', '- Css [Pa/mNm]', '- Start Delay Time [s]',
 '- Substance Density [rho]', '- Measurement Type', '- Motor Correction Factor',
 '- Axial Compliance [m/N]']
imd_constants=['Number of Data Points']

def nm2lbl(path):
	return 'R:{} i:{}'.format(path.split('/')[-2][-1], path.split('/')[-1][-6:-4])

def cleanstr(i):
	toclean=''.join(['\t','\r','\n','\xb0',','])
	return i.translate(None, toclean)

def cleanfname(i):
	trns=string.maketrans(' ;/\\','----')
	return i.translate(trns)

def mkdir_safe(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise

def fix_columns(i_data, i_metadata):
	okay_clm_idcs=[i for i in range(0,np.shape(i_data)[1]) if not any(np.array(i_data)[:,i] == '******')]
	headers=np.array(i_metadata['Header'])[okay_clm_idcs]
	units=np.array(i_metadata['Units'])[okay_clm_idcs]
	datas=np.array(i_data)[:,okay_clm_idcs]
	return datas, headers, units

def fix_rows(i_data):
	i_data=np.array([[n for n in row] for row in i_data if not any(np.array(row)=='invalid point')])
#	okay_row_idcs=[i for i in range(0,np.shape(i_data)[0]) if not any(np.array(i_data[i])=='invalid point')\
#			or any(np.array(i_data[i])=='') ]

	return i_data

def open_rhe(filename):
	with open(filename) as f:
		header=[cleanstr(i) for i in f.readline().split("# ")[1].split('\t')]
		units=[cleanstr(i) for i in f.readline().split("# ")[1].split('\t')]
	datas=np.loadtxt(filename)
	return datas, header, units

def check_columns(filename, columns):
	datas, header, units=open_rhe(filename)
	truth=[column in header for column in columns]
	truthdict={column:column in header for column in columns}
	if not all(truth): 
		print('# Some columns where not found: {}'.format(' '.join([i for i in truthdict if truthdict[i]==False])))
		print('# Offending filename: {}'.format(filename))
		raise(ValueError('One or more columns in the input are not found in the datafile(s).'))
	if all(truth): return True
	return None

def get_columns(filename, columns):
	datas, header, units=open_rhe(filename)
	clm_idcs=[ header.index(column) for column in columns  ]
	stack=np.vstack([ datas[:,i] for i in clm_idcs  ]).transpose()
	header=[ header[i] for i in clm_idcs  ]
	return stack

def write_rheodicts(dsi_metadatas, i_metadatas, i_datas):
	for name in dsi_metadatas:
		mkdir_safe(cleanfname(name))
		metadatalist=['{}:{}'.format(key, dsi_metadatas[name][key]) for key in dsi_metadatas[name] ]
		metadatalist.append('\n')
		metadatalist.append('-----')
		for i in i_metadatas[name]:
			metadatalist.append("Interval {}".format(i))
			for key in i_metadatas[name][i]:
				metadatalist.append('{}:{}'.format(key, i_metadatas[name][i][key]))
			metadatalist.append('\n')
			metadatalist.append('-----')

		np.savetxt(cleanfname(name)+'-dsi.txt', metadatalist, fmt='%s')
		for interval in i_datas[name]:
			i_data=i_datas[name][interval]
			i_metadata=i_metadatas[name][interval]
			i_data=fix_rows(i_data)
			i_data, header, units=fix_columns(i_data, i_metadata)
			filehead='\t'.join(header)+"\n"
			filehead+='\t'.join(units)
			np.savetxt(cleanfname(name)+'/int'+format(int(interval),'05d')+'.rhe', i_data, fmt="%s", header=filehead)

def openrheo(filename):
	unannotated_metadata_counter=0
	metadatas={}
	dsi_metadatas={}
	i_metadatas={}
	i_datas={}
	f=open(filename)
	datas=[]
	in_dsi=False; in_imd=False; in_id=False;
	for line in f:
		if in_dsi==False:
			splitline=line.split('\r')
			splitlinen=line.split('\n')
			if "Data Series Information" in line:
				in_dsi=True
				continue

		if in_dsi==True:
			splitline=line.split(':')
			if splitline[0]=="Interval":
				current_dsi_name=metadatas['Name']
				dsi_metadatas[current_dsi_name]=metadatas
				i_metadatas[current_dsi_name]={}
				i_datas[current_dsi_name]={}
				metadatas={}
				in_dsi=False
				in_imd=True
				current_interval=1
				continue
			if splitline[0] in dsi_constants: 
				metadatas[splitline[0]]=cleanstr(splitline[-1])
		
		if in_imd==True:
			splitcolon=line.split(':')
			splitspace=line.split(' ')
			splittab=line.split('\t')
			if splitspace[0]=='Meas.':
				metadatas['Header']=[cleanstr(i) for i in splittab]
				i_metadatas[current_dsi_name][current_interval]=metadatas
				metadatas={}
				in_imd=False
				in_id=True
				unannotated_metadata_counter=0
				continue
			if splitcolon[0] in imd_constants:
				metadatas[splitcolon[0]]=cleanstr(splitcolon[-1])
			elif cleanstr(line) != '':
				metadatas['{}'.format(unannotated_metadata_counter)]=cleanstr(line)
				unannotated_metadata_counter+=1

		if in_id==True:
			splittab=line.split('\t')

			# is the last entry reached?
			if cleanstr(str(splittab[0]))==cleanstr(i_metadatas[current_dsi_name][current_interval]["Number of Data Points"]):
				datas.append([cleanstr(i) for i in splittab])
				i_datas[current_dsi_name][current_interval]=datas[1:]
				i_metadatas[current_dsi_name][current_interval]["Units"]=datas[0]
				current_interval+=1
				# TODO: YES we must clean up the columns
				in_id=False
				in_imd=True # which does not mean that the code would get executed!
				datas=[]
				continue
			datas.append([cleanstr(i) for i in splittab])
			# we parse the metadata until there is none
	return dsi_metadatas, i_metadatas, i_datas	

#def openrheo(filename):
#	data=[[]]
#	with open(filename) as f:
#		for line in f:
#			data.append(line)
#	samples=[[data[i].split(":")[1],i] for i in xrange(0,len(data)) \
#			if data[i]!=[] and (data[i].split(":")[0]=="Name" or\
#			data[i].split(":")[0]=="Interval")]
#	samples.append(["end", len(data)])
#	rngs=[(samples[i-1][1],samples[i][1]-3) for i in range(1,len(samples))]
#	print rngs
#	
#	blocks={}
#	for rng in rngs:
#		found_block=False
#		block=[[]]
#		for line in data[rng[0]:rng[1]]:
#			if line!=[] and line.split()[0]=='Meas.': found_block=True
#			if found_block==True: block.append(line.split(","))
#		blocks[rng]=block
#	print "Found"
#	print samples
#	return blocks
