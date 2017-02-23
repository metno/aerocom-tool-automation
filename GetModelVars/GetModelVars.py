#!/usr/bin/env python3

################################################################
# GetModelVars.py
#
# program ito find the variables a model directory contains
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

def GetModelVars(ModelFolder, VerboseFlag=False, DebugFlag=False):
	#unfortunately there's more than one file naming convention
	#examples
	#aerocom3_CAM5.3-Oslo_AP3-CTRL2016-PD_od550aer_Column_2010_monthly.nc
	#aerocom.AATSR_ensemble.v2.6.daily.od550aer.2012.nc
	if os.path.isdir(ModelFolder):
		Vars=[]
		files=glob.glob(ModelFolder+'/*.nc')
		for file in files:
			#divide the type based on the # of underscores in a file name
			if os.path.basename(file).count('_') >= 4:
				#newest file naming convention
				c_DummyArr=file.split('_')
				Vars.append(c_DummyArr[-4])
			elif os.path.basename(file).count('.') >= 4:
				c_DummyArr=file.split('.')
				Vars.append(c_DummyArr[-3])

		#make sorted list of unique years
		Vars=(sorted(OrderedDict.fromkeys(Vars)))

		if VerboseFlag:
			print(Vars)
		if DebugFlag:
			pdb.set_trace()

	return Vars


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Return the variables in an aerocom model directory\n\n')
	parser.add_argument("dir", help="directory to check")

	args = parser.parse_args()
	if args.dir:
		Vars=GetModelVars(args.dir, DebugFlag=False)
		if len(Vars) > 0:
			sys.stdout.write('\n'.join(Vars)+'\n')
		else:
			sys.exit(1)



