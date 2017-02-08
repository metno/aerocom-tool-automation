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

def GetModelYears(ModelFolder, Variable=None, VerboseFlag=False, DebugFlag=False):
	if os.path.isdir(ModelFolder):
		Years=[]
		if Variable == None:
			files=glob.glob(ModelFolder+'/*.nc')
		else:
			files=glob.glob(ModelFolder+'/*.'+Variable+'.*.nc')
		for file in files:
			c_DummyArr=file.split('.')
			Years.append(c_DummyArr[-2])

		#make sorted list of unique years
		Years=(sorted(OrderedDict.fromkeys(Years)))

		if VerboseFlag:
			print(Years)
		if DebugFlag:
			pdb.set_trace()

	return Years


if __name__ == '__main__':
	ModelFolder='/lustre/storeB/project/aerocom/aerocom-users-database/CCI-Aerosol/CCI_AEROSOL_Phase2/AATSR_ensemble.v2.6/renamed'
	Years=GetModelYears(ModelFolder, Variable='od550aer')
	print(Years)

