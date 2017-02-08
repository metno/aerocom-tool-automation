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


def GetModelDirsToWorkOn(MaxTimeDiffDays, VerboseFlag=False, DebugFlag=False, c_ConfigFile=None ):
	if c_ConfigFile == None:
		c_ConfigFile='folders.ini'
	dict_Config={}
	now=time.time()
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
				print(FolderToSearchIn)
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
									print(dir)
									print('difference to now: ',(now - os.path.getmtime(dir))/60./60./24.,' days')

		if VerboseFlag:
			print(DirsToWorkOn)
		if DebugFlag:
			pdb.set_trace()

	return DirsToWorkOn


if __name__ == '__main__':
	MaxTimeDiffDays=2.
	DirsToWorkOn=GetModelDirsToWorkOn(MaxTimeDiffDays, VerboseFlag=False)
	print(DirsToWorkOn)

