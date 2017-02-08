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

def GetModelVars(ModelFolder, VerboseFlag=False, DebugFlag=False):
	if os.path.isdir(ModelFolder):
		Vars=[]
		files=glob.glob(ModelFolder+'/*.nc')
		for file in files:
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
	ModelFolder='/lustre/storeB/project/aerocom/aerocom-users-database/CCI-Aerosol/CCI_AEROSOL_Phase2/AATSR_ensemble.v2.6/renamed'
	Vars=GetModelVars(ModelFolder)
	print(Vars)

