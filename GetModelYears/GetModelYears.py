#!/usr/bin/env python3

################################################################
# GetModelYears.py
#
# program find the years a model directory contains
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import os
import glob
from collections import OrderedDict
import argparse
import sys

def GetModelYears(ModelFolder, Variable=None, VerboseFlag=False, DebugFlag=False):
	#unfortunately there's more than one file naming convention
	#examples
	#aerocom3_CAM5.3-Oslo_AP3-CTRL2016-PD_od550aer_Column_2010_monthly.nc
	#aerocom.AATSR_ensemble.v2.6.daily.od550aer.2012.nc
	Years=[]
	if os.path.isdir(ModelFolder):
		if Variable == None:
			files=glob.glob(ModelFolder+'/*.nc')
		else:
			files=glob.glob(ModelFolder+'/*'+Variable+'*.nc')
		for file in files:
			#divide the type based on the # of underscores in a file name
			if os.path.basename(file).count('_') >= 4:
				#newest file naming convention
				c_DummyArr=file.split('_')
				Years.append(c_DummyArr[-2])
			elif os.path.basename(file).count('.') >= 4:
				c_DummyArr=file.split('.')
				Years.append(c_DummyArr[-2])

		#make sorted list of unique years
		Years=(sorted(OrderedDict.fromkeys(Years)))

	else:
		sys.stderr.write("Error: Model folder does not exist: \n")
		sys.stderr.write(ModelFolder+"\n")
		sys.stderr.write('Exiting.\n')
		sys.exit(3)


	if VerboseFlag:
		print(Years)
	if DebugFlag:
		pdb.set_trace()

	return Years


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Return the data years in an aerocom model directory\n\n')
	parser.add_argument("dir", help="directory to check")
	parser.add_argument("--var", help="return the years for a given variable")
	parser.add_argument("--commasep", help="set to 1 to get a comma separated list")
	args = parser.parse_args()
	Var=None
	if args.var:
		Var=args.var

	Years=GetModelYears(args.dir, Variable=Var)
	if args.dir:
		if len(Years) > 0:
			if args.commasep:
				sys.stdout.write(','.join(Years)+'\n')
			else:
				sys.stdout.write('\n'.join(Years)+'\n')
		else:
			sys.exit(1)

