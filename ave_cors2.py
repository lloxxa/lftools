#!/bin/python

import fileinput
import lftools as lf
import numpy as np
import os, sys
import StringIO

def main(*args):
	dirname=os.getcwd().split('/')[-1]

	s=StringIO.StringIO()

	ascfiles=lf.openseries_fl(args)
	corfs={name:np.vstack([ascfiles[0][name][:,0], np.average(ascfiles[0][name][:,1:3],1)]).transpose() for name in ascfiles[0]}
	taus=corfs[corfs.keys()[0]][:,0]
	rawcorfs=np.vstack([ corfs[name][:,1] for name in sorted(corfs.keys()) ]).transpose()
	avecorf=np.average(np.vstack(corfs[i][:,1] for i in corfs).transpose(),1)
	rescaled_avecorf=avecorf/avecorf[0]
	first_columns=np.vstack([taus, rescaled_avecorf, avecorf])
	last_columns=np.vstack([column for column in rawcorfs.transpose()])
	corfdata=np.vstack([first_columns, last_columns]).transpose()

	condistring="Average correlation over files {}".format(' '.join(args))
	headerstring="tau/(ms) (g2-1)/g2_0_(tau) (g2-1)_(tau) "+' '.join(sorted(corfs.keys()))
	np.savetxt(s, corfdata, header=condistring+'\n'+headerstring)
	
	sys.stdout.write(s.getvalue())

if __name__=='__main__':
	# no roomfor options at the moment. but maybe in the future
	args=[]
	for line in fileinput.input():
		files=(line.split(' '))
		for i in files: args.append(i.replace('\n',''))

	print("# " + ' '.join(args))
	main(*args)
