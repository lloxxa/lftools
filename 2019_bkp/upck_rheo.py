#!/bin/python
import glob as gl
import rheotools as rt
import os

def main():
	files=gl.glob("*.txt")
	for f in [fi for fi in files if "-dsi.txt" not in fi]:
		print(f)
		a,b,c=rt.openrheo(f)
		rt.write_rheodicts(a,b,c)
		os.rename(f, f.split(".txt")[0]+".ssd")

if __name__=='__main__':
	main()
