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
import glob
import argparse 
import sys



def GetModelDir(ModelArr, VerboseFlag=False, DebugFlag=False, c_ConfigFile=None ):
	if c_ConfigFile == None:
		c_ConfigFile='../folders.ini'
	dict_Config={}
	ModelDirs={}
	if os.path.isfile(c_ConfigFile):
		ReadConfig = configparser.ConfigParser()
		ReadConfig.read(c_ConfigFile)
		dict_Config['BaseDir']=[ReadConfig['folders']['BASEDIR']]
		dict_Config['FoldersToSearchIn']=ReadConfig['folders']['dir'].replace('${BASEDIR}',dict_Config['BaseDir'][0]).replace('\n','').split(',')

		#Return only folders containing renamed at the end
		#This way we are sure to find only model dirs likely containing data
		
		for ModelName in ModelArr:
			#loop through the list of models
			for FolderToSearchIn in dict_Config['FoldersToSearchIn']:
				if VerboseFlag:
					print('Searching in: ',FolderToSearchIn)
				#get the directories
				if os.path.isdir(FolderToSearchIn):
					dir=glob.glob(FolderToSearchIn+ModelName)
					if len(dir) > 0:
						ModelDirs[ModelName]=dir[0]
						if VerboseFlag:
							print('Found: ',ModelDirs[ModelName])
						break
					else:
						continue
				else:
					if VerboseFlag:
						print('directory: ',FolderToSearchIn, ' does not exist')
					
		if VerboseFlag:
			print(ModelDirs)
		if DebugFlag:
			pdb.set_trace()

	return ModelDirs


if __name__ == '__main__':
	dict_Param={}
	parser = argparse.ArgumentParser(description='GetModelDir\nProgram to find the actual model for a given model name\n\n')
	parser.add_argument("model", help="model names to use; can be a comma separated list;")
	parser.add_argument("--config", help="use another config file")
	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.model:
		dict_Param['ModelName']=args.model.split(',')

	dict_Param['ConfigFile']=False
	if args.config:
		if os.path.isfile(args.config): 
			dict_Param['ConfigFile']=args.config
		else:
			sys.stderr.write('Error: The supplied config file does not exist. Exiting.\n')
			sys.exit(1)

	ModelDirs=GetModelDir(dict_Param['ModelName'], VerboseFlag=False)
	for Model in ModelDirs.keys():
		sys.stdout.write(':'.join([Model,ModelDirs[Model]])+'\n')

