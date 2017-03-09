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
	Vars=[]
	if os.path.isdir(ModelFolder):
		files=glob.glob(ModelFolder+'/*.nc')
		for file in files:
			#divide the type based on the # of underscores in a file name
			if os.path.basename(file).count('_') >= 4:
				#newest file naming convention
				c_DummyArr=file.split('_')
				# include vars for the surface
				if c_DummyArr[-3].lower() == 'surface':
					Vars.append(c_DummyArr[-4])
				#also include 3d vars that provide station based data
				#and contain the string vmr
				#in this case the variable name has to slightly changed to the aerockm phase 2 naming
				elif c_DummyArr[-3].lower() == 'modellevelatstations':
					if 'vmr' in c_DummyArr[-4]:
						Vars.append(c_DummyArr[-4].replace('vmr','vmr3d'))
			elif os.path.basename(file).count('.') >= 4:
				c_DummyArr=file.split('.')
				Vars.append(c_DummyArr[-3])

		#make sorted list of unique years
		Vars=(sorted(OrderedDict.fromkeys(Vars)))

		if VerboseFlag:
			print(Vars)
		if DebugFlag:
			pdb.set_trace()
	else:
		sys.stderr.write("Error: Model folder does not exist: \n")
		sys.stderr.write(ModelFolder+"\n")
		sys.stderr.write('Exiting.\n')
		sys.exit(3)

	return Vars


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Return the variables in an aerocom model directory. Note that for the aerocom phase 3 naming scheme we return only surface variables and those that provide 3d data at stations (the file name contains the string "ModelLevelAtStations").\n')
	parser.add_argument("dir", help="directory to check")

	args = parser.parse_args()
	if args.dir:
		Vars=GetModelVars(args.dir, DebugFlag=False)
		if len(Vars) > 0:
			sys.stdout.write('\n'.join(Vars)+'\n')
		else:
			sys.exit(1)



