#!/usr/bin/env python3

################################################################
# GetNewFolder.py
#
# program to find the newly uploaded models to the aerocom data base
#
# Uses an ini file with the directories to search in for new model directories
# These are characterised as ending with the string 'renamed'
#
# The ini file looks like this
# #folder.ini
# #ini file that defines the folders to be searched in
# 
# [folders]
# BASEDIR=/lustre/storeB/project/aerocom/
# dir=${BASEDIR}aerocom-users-database/ECMWF/,
  # ${BASEDIR}aerocom1/,
  # ${BASEDIR}aerocom2/
# 
# ${BASEDIR} replaced with the string assigned to BASEDIR in the program
#################################################################
# Created 20170202 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import configparser
import os
import time
import re
import argparse
import sys



def GetModelDirsToWorkOn(MaxTimeDiffDays, VerboseFlag=False, DebugFlag=False, c_ConfigFile=None):
	if c_ConfigFile == None:
		c_ConfigFile=os.path.join(os.path.dirname(os.path.realpath(__file__)),'../constants.ini')
		#pdb.set_trace()
	dict_Config={}
	now=time.time()
	if VerboseFlag:
		sys.stderr.write('reading config file :'+c_ConfigFile+'\n')
	if os.path.isfile(c_ConfigFile):
		ReadConfig = configparser.ConfigParser()
		ReadConfig.read(c_ConfigFile)
		dict_Config['BaseDir']=[ReadConfig['folders']['BASEDIR']]
		dict_Config['FoldersToSearchIn']=ReadConfig['folders']['dir'].replace('${BASEDIR}',dict_Config['BaseDir'][0]).replace('\n','').split(',')

		DirsToWorkOn=[]
		#Return only folderd containing renamed at the end
		#This way we are sure to find only model dirs likely containing data
		MatchPattern=re.compile('.*/renamed$')
		for FolderToSearchIn in dict_Config['FoldersToSearchIn']:
			if VerboseFlag:
				sys.stderr.write('checking '+FolderToSearchIn+' ...\n')
			#get the directories
			if os.path.isdir(FolderToSearchIn):
				SubDirs=[x[0] for x in os.walk(FolderToSearchIn)]
				for dir in SubDirs:
					#unfortunately FolderToSearchIn appears here as well
					if dir != FolderToSearchIn:
						#look for folders according to MatchPattern
						if MatchPattern.match(dir):
							DiffDays=(now - os.path.getmtime(dir))/360./24.
							if DiffDays <= MaxTimeDiffDays:
								DirsToWorkOn.append(dir)
								if VerboseFlag:
									sys.stderr.write(dir+'\n')
									#pdb.set_trace()
									#sys.stderr.write('difference to now: '+str(now - os.path.getmtime(dir))/60./60./24.,+' days'+'\n')
									sys.stderr.write('difference to now: {:5.2f} days'.format(DiffDays)+'\n')

		if DebugFlag:
			pdb.set_trace()

	return DirsToWorkOn


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='aerocom-automation-tools: GetNewFolder.py\nProgram to find the newest models.\n\n')
	parser.add_argument("--age", help="max file age in days. Defaults to 2.",default=2)
	parser.add_argument("--verbose", help="switch on verbosity",action='store_true')
	parser.add_argument("--listmodels", help="list just the model name, not the model folder.",action='store_true')
	#parser.add_argument("--modelyear", help="model years to run; use 9999 for climatology, leave out for all years; comma separated list")

	args = parser.parse_args()

	if args.listmodels:
		ListModels=True
	else:
		ListModels=False
	
	if args.verbose:
		VerboseFlag=True
	else:
		VerboseFlag=False
	
	if args.age:
		MaxTimeDiffDays=int(args.age)
		if VerboseFlag is True:
			sys.stderr.write('searching for dirs up to '+str(MaxTimeDiffDays)+' days old.\n')
	
	#MaxTimeDiffDays=2.
	#pdb.set_trace()
	DirsToWorkOn=GetModelDirsToWorkOn(MaxTimeDiffDays, VerboseFlag=VerboseFlag)
	if ListModels is False:
		for Dir in DirsToWorkOn:
			sys.stdout.write(Dir+'\n')
	else:
		for Dir in DirsToWorkOn:
			DummyArr=Dir.split('/')
			sys.stdout.write(DummyArr[-2]+'\n')
			

