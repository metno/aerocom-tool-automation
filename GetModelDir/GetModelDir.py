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
import subprocess



def GetModelDir(ModelArr, VerboseFlag=False, DebugFlag=False, c_ConfigFile=None ):
	if c_ConfigFile == None:
		c_ConfigFile='folders.ini'
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
						ModelDirs[ModelName]=dir
						if VerboseFlag:
							print('Found: ',ModelDirs[ModelName])
						#break
					else:
						continue
				else:
					if VerboseFlag:
						print('directory: ',FolderToSearchIn, ' does not exist')
					
	else:
		sys.stderr.write('Error: Config file '+c_ConfigFile+' not found. Exiting.\n')
		sys.exit(2)

	if VerboseFlag:
		print(ModelDirs)
	if DebugFlag:
		pdb.set_trace()

	return ModelDirs


if __name__ == '__main__':
	dict_Param={}
	parser = argparse.ArgumentParser(description='GetModelDir: Program to find the actual model directory for a given model name\n\n',
	epilog='Returns a colon separated list for each given model')
	parser.add_argument("model", help="model names to use; can be a comma separated list; shell wildcards can be used")
	parser.add_argument("-c","--config", help="use another config file; ./folder.ini if not given", default='folders.ini')
	parser.add_argument("-l","--list", help="list files in model directory", action='store_true')
	#parser.add_argument("-l", help="")

	args = parser.parse_args()

	if args.list:
		dict_Param['ls']=args.list
	else:
		dict_Param['ls']=False

	if args.model:
		dict_Param['ModelName']=args.model.split(',')

	dict_Param['ConfigFile']=False
	if args.config:
		#pdb.set_trace()
		if os.path.isfile(args.config): 
			dict_Param['ConfigFile']=args.config
		else:
			#try script directory
			IniPath=os.path.join(os.path.dirname(sys.argv[0]),args.config)
			pdb.set_trace()
			if not os.path.isfile(IniPath):
				sys.stderr.write('Error: The supplied config file does not exist. Exiting.\n')
				sys.exit(1)
			else:
				dict_Param['ConfigFile']=IniPath

	ModelDirs=GetModelDir(dict_Param['ModelName'], c_ConfigFile=dict_Param['ConfigFile'])
	for Model in ModelDirs:
		if dict_Param['ls'] is False:
			sys.stdout.write(':'.join([Model,','.join(ModelDirs[Model])])+'\n')
		else:
			#pdb.set_trace()
			#model could be on the fs on more than one directory
			if len(ModelDirs[Model]) > 1:
				sys.stderr.write('WARNING: Model found on more than obe directory!\n')
			for dir in ModelDirs[Model]:
				for file in sorted(os.listdir(os.path.join(dir,'renamed'))):
					sys.stdout.write(file+'\n')

