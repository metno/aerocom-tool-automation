#!/usr/bin/env python3

################################################################
# aerocom-tool-automation.py
#
# main program of the aerocom-tool-automation software
# 
# The purpose of this program is to plot all possible plots of a new 
# model version
# it takes a model name as parameter
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import GetNewFolder
import GetModelVars
import GetModelYears
import GetModelDir
import WriteIDLIncludeFile
import argparse 
import sys
import os
import subprocess
import getpass
import multiprocessing
from time import sleep
import ModAerocomMain
import datetime
import socket
import helpers.Taskinfo as Taskinfo
import helpers.ReadIniFile as ReadIniFile
import GetObsNetworkSupportedVars


###################################################################################


if __name__ == '__main__':
	import configparser

	#get all supported obs networks to use that in the text
	dict_SupportStruct=WriteIDLIncludeFile.GetIDLIncludeFileText('nogroup','whatever', all=True)
	SupportedObsNetworks=', '.join(sorted(dict_SupportStruct['OBSNETWORKS'].keys()))

	#Read Ini file for some parameters
	ConfigIni=os.path.join(os.path.dirname(os.path.realpath(__file__)),'constants.ini')
	IniFileData=configparser.ConfigParser()
	IniFileData.read(ConfigIni)
	ObsOnlyModelName=IniFileData['parameters']['ObsOnlyModelname']

	#command line interface using argparse
	dict_Param={}
	parser = argparse.ArgumentParser(description='aerocom-automation-tools\nProgram to automate aerocom-tool plotting based on just the model name\n\n')
	parser.add_argument("model", help="model names to use; can be a comma separated list;use "+ObsOnlyModelName+" for observations only")
	parser.add_argument("--variable", help="Run only a list of variables. List has to be comma seperated.")
	parser.add_argument("--modelyear", help="model years to run; use 9999 for climatology, leave out for all years; comma separated list")
	parser.add_argument("--obsyear", help="observation years to run; use 9999 for climatology, leave out for same as model year")
	parser.add_argument("--tooldir", help="set the directory of the aerocom-tools; if unset ${HOME}/aerocom-tools/ will be used")
	parser.add_argument("--nosend", help="switch off webserver upload",action='store_true')
	parser.add_argument("-p","--print", help="switch on idl include file name printing to stdout. Might be useful for external programs",action='store_true')
	parser.add_argument("-v","--verbose", help="switch on verbosity",action='store_true')
	parser.add_argument("--script", help="script to start; defaults to <tooldir>/StartScreenWithLogging.sh")
	parser.add_argument("--debug", help="switch on debug mode: Do NOT start idl, just print what would be done",action='store_true')
	parser.add_argument("--numcpu", help="Number of Processes to start. Default is using half of the number of logical cores available.",type=int)
	parser.add_argument("--idl", help="location of the idl binary. Uses $IDL_DIR/bin/idl as default")

	parser.add_argument("--outputdir", help="directory where the idl include files will be put. Default is <tooldir>/batching. Directory needs to exist.")
	parser.add_argument("--obsnetwork", help="run all variables for a certain obs network; Supported are "+SupportedObsNetworks)
	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.numcpu:
		dict_Param['NumCPU']=args.numcpu

	if args.variable:
		dict_Param['VariablesToRun']=args.variable.split(',')

	if args.model:
		dict_Param['ModelName']=args.model.split(',')


	if args.idl:
		dict_Param['IDL']=args.idl
	else:
		dict_Param['IDL']=os.path.join(os.environ['IDL_DIR'],'bin','idl')
		if os.path.isfile(dict_Param['IDL']) is False:
			sys.stderr.write('Error: idl not found!\n')
			sys.stderr.write('Path: '+dict_Param['IDL']+'\n')
			sys.stderr.write('Please supply the correct location with the --idl switch\n')

	if args.debug:
		dict_Param['DEBUG']=args.debug
	else:
		dict_Param['DEBUG']=False

	if args.print:
		dict_Param['PRINT']=args.print
	else:
		dict_Param['PRINT']=False

	if args.nosend:
		dict_Param['NOSEND']=args.nosend
	else:
		dict_Param['NOSEND']=False

	if args.verbose:
		dict_Param['VERBOSE']=args.verbose
	else:
		dict_Param['VERBOSE']=False

	if args.tooldir:
		dict_Param['ToolDir']=args.tooldir
	else:
		dict_Param['ToolDir']=os.path.join(os.environ['HOME'],'aerocom-tools')
	if os.path.isdir(dict_Param['ToolDir']) is False:
		sys.stderr.write('Error: supplied tool dir does not exist.\n')
		sys.exit(1)
	
	if args.script:
		dict_Param['SCRIPT']=args.script
	else:
		dict_Param['SCRIPT']=os.path.join(dict_Param['ToolDir'],'StartScreenWithLogging.sh')

	if args.obsyear:
		dict_Param['ObsYear']=args.obsyear
	else:
		dict_Param['ObsYear']='0000'

	if args.modelyear:
		dict_Param['ModelYear']=args.modelyear.split(',')
	else:
		dict_Param['ModelYear']='all'

	if args.outputdir:
		if os.path.isdir(args.outputdir):
			dict_Param['OutputDir']=args.outputdir
		else:
			sys.stderr.write('Error: supplied output dir for idl include files does not exist.\n')
			sys.exit(2)
	else:
		dict_Param['OutputDir']=os.path.join(dict_Param['ToolDir'],'batching')

	if args.obsnetwork:
		dict_Param['ObsnetworksToRun']=args.obsnetwork.split(',')[0]
		#use the 1st for model plotting for now
		dict_Param['ObsNetworkName']=args.obsnetwork.split(',')[0]

	hostname=socket.gethostname()
	CmdArr=[]
	#handle the OBSERVATIONS-ONLY case
	#if this model is part of the model list we switch to obs only mode
	#no other models will be plotted for now
	if ObsOnlyModelName in dict_Param['ModelName']:
		#change the variables to run to the ones provided by the obs network chosen
	
		if not args.obsnetwork:
			sys.stderr.write('Error: no observations network given. \nPlease use the --obsnetwork switch to set one. \nSupported are '+SupportedObsNetworks+'\n')
			sys.exit(3)
		else:
			Model=ObsOnlyModelName
			dict_Param['ObsnetworksToRun']=args.obsnetwork.split(',')
			for ObsNetWork in dict_Param['ObsnetworksToRun']:
				#determine variables
				dict_Param['ObsNetworkName']=ObsNetWork

				Vars=GetObsNetworkSupportedVars.GetObsNetworkSupportedVars(dict_Param['ToolDir'],ObsNetWork)
				for Var in Vars:
					if args.variable:
						if Var not in dict_Param['VariablesToRun']:
							if dict_Param['VERBOSE'] is True:
								sys.stderr.write('Var '+Var+' not in provided list of vars to run. Skipping that variable.\n')
							continue

					try:
						Dummy=dict_SupportStruct['VARS'][Var]
					except KeyError:
						if dict_Param['VERBOSE'] is True:
							sys.stderr.write('WARNING: Variable "'+Var+'" not supported by the aerocom-automation-tools\n')
							sys.stderr.write('Continuing with the other variables.\n')
						continue

					#now write the idl include file
					#one per variable
					dict_Param['IDLOutFile']=os.path.join(dict_Param['OutputDir'],ObsNetWork+'_'+Var+'_include.pro')
					dict_Param['VarName']=Var
					#Maybe we want to check if the variable is actually supported
					ModellistFile=os.path.join(dict_Param['ToolDir'],'batching', ObsNetWork+'_'+Var+'.txt')
					#write IDL include file
					try:
						WriteIDLIncludeFile.WriteIDLIncludeFile(dict_Param)
					except SystemExit:
						pass

					#Get obs years from config file
					try:
						ObsStartYear=int(IniFileData['ObsStartYears'][ObsNetWork])
					except:
						ObsStartYear=int(IniFileData['ObsStartYears']['All'])
						
					#pdb.set_trace()
					Years=list(map(str,range(ObsStartYear,2018)))

					if dict_Param['VERBOSE'] == True:
						sys.stderr.write('File "'+dict_Param['IDLOutFile']+'" written\n')
						#sys.stderr.write('File "'+ModellistFile+'" written\n')
					if dict_Param['PRINT'] == True:
						sys.stdout.write(dict_Param['IDLOutFile']+'\n')
						#sys.stdout.write(ModellistFile+'\n')

					for Year in Years:
						if args.modelyear:
							if Year not in dict_Param['ModelYear']:
								if dict_Param['VERBOSE'] is True:
									sys.stderr.write('Year '+Year+' not in provided list of Years to run. Skipping that Year.\n')
								continue
								
						if dict_Param['VERBOSE'] == True:
							sys.stderr.write('Year: '+Year+'\n')

						#Create an array with program calls for IDL
						#pdb.set_trace()
						OutFile, IncFile=ModAerocomMain.ModAerocomMain(dict_Param['ToolDir'], dict_Param['IDLOutFile'])
						if not os.path.isfile(OutFile):
							pdb.set_trace()
						if not os.path.isfile(IncFile):
							pdb.set_trace()
						#IDL does not like the filename ending with '.pro', so remove that
						OutFile=OutFile.replace('.pro','')
						IdlCmd=OutFile+",modelin=['"+Model+"'],yearin=['"+Year+"'],datayearin='"+dict_Param['ObsYear']+"'"
						SessionName='_'.join([Model,Var,Year,hostname])
						cmd=['/bin/bash',dict_Param['SCRIPT'], '-d', '-L', '-m', '-S', SessionName, dict_Param['IDL'], '-queue', '-e' , IdlCmd]
						#cmd=[dict_Param['SCRIPT'], '-d', '-L', '-m', dict_Param['IDL'], '-queue', '-e' , IdlCmd]
						CmdArr.append(cmd)

	else:
		#model plotting mode
		#get the folder the data is located in for each model
		#non existing models are ignored and there will be no error
		#message unless one model is present
		#returns a list
		ModelFolders=GetModelDir.GetModelDir(dict_Param['ModelName'],
			c_ConfigFile=ConfigIni, VerboseFlag=False)

		#get the supported variables list
		dict_SupportStruct=WriteIDLIncludeFile.GetIDLIncludeFileText('nogroup','whatever', all=True)
		SupportedVars=','.join(sorted(dict_SupportStruct['VARS'].keys()))
		#loop through the model dirs
		Models=list(ModelFolders.keys())
		for Model in ModelFolders.keys():
			#just the 1st model dir for now
			Modeldir=os.path.join(ModelFolders[Model][0],'renamed')
			Vars=GetModelVars.GetModelVars(Modeldir)
			if dict_Param['VERBOSE'] == True:
				sys.stderr.write('Modeldir: '+Modeldir+'\n')
			#loop through the Variables an determine the years they are present
			for Var in Vars:
				if args.variable:
					if Var not in dict_Param['VariablesToRun']:
						if dict_Param['VERBOSE'] is True:
							sys.stderr.write('Var '+Var+' not in provided list od vars to run. Skipping that variable.\n')
						continue

				try:
					Dummy=dict_SupportStruct['VARS'][Var]
				except KeyError:
					if dict_Param['VERBOSE'] is True:
						sys.stderr.write('WARNING: Variable "'+Var+'" not supported by the aerocom-automation-tools\n')
						sys.stderr.write('Continuing with the other variables.\n')
					continue

					
				#now write the idl include file
				#one per variable
				dict_Param['IDLOutFile']=os.path.join(dict_Param['OutputDir'],Model+'_'+Var+'_include.pro')
				dict_Param['VarName']=Var
				#Maybe we want to check if the variable is actually supported
				ModellistFile=os.path.join(dict_Param['ToolDir'],'batching', Model+'_'+Var+'.txt')
				#write IDL include file
				try:
					WriteIDLIncludeFile.WriteIDLIncludeFile(dict_Param)
				except SystemExit:
					pass

				Years=GetModelYears.GetModelYears(Modeldir, Variable=Var)
				#c_Years=','.join(Years)
				#try:
				#	WriteIDLIncludeFile.WriteModellistFile(ModellistFile, Model, c_Years, dict_Param['ObsYear'])
				#except SystemExit:
				#	pass
					
				if dict_Param['VERBOSE'] == True:
					sys.stderr.write('File "'+dict_Param['IDLOutFile']+'" written\n')
					#sys.stderr.write('File "'+ModellistFile+'" written\n')
				if dict_Param['PRINT'] == True:
					sys.stdout.write(dict_Param['IDLOutFile']+'\n')
					#sys.stdout.write(ModellistFile+'\n')

				for Year in Years:
					if args.modelyear:
						if Year not in dict_Param['ModelYear']:
							if dict_Param['VERBOSE'] is True:
								sys.stderr.write('Year '+Year+' not in provided list of Years to run. Skipping that Year.\n')
							continue
					if dict_Param['VERBOSE'] == True:
						sys.stderr.write('Year: '+Year+'\n')

					#Create an array with program calls for IDL
					#pdb.set_trace()
					OutFile, IncFile=ModAerocomMain.ModAerocomMain(dict_Param['ToolDir'], dict_Param['IDLOutFile'])
					if not os.path.isfile(OutFile):
						pdb.set_trace()
					if not os.path.isfile(IncFile):
						pdb.set_trace()
					#IDL does not like the filename ending with '.pro', so remove that
					OutFile=OutFile.replace('.pro','')
					IdlCmd=OutFile+",modelin=['"+Model+"'],yearin=['"+Year+"'],datayearin='"+dict_Param['ObsYear']+"'"
					SessionName='_'.join([Model,Var,Year,hostname])
					cmd=['/bin/bash',dict_Param['SCRIPT'], '-d', '-L', '-m', '-S', SessionName, dict_Param['IDL'], '-queue', '-e' , IdlCmd]
					#cmd=[dict_Param['SCRIPT'], '-d', '-L', '-m', dict_Param['IDL'], '-queue', '-e' , IdlCmd]
					CmdArr.append(cmd)

	

	#common part
	user = getpass.getuser()
	try:
		MaxNumOfTasksToStart=dict_Param['NumCPU']
	except KeyError: 
		MaxNumOfTasksToStart=multiprocessing.cpu_count()/2

	taskinfo=Taskinfo('.*idl', user=user, RetNumber=True,)

	if dict_Param['DEBUG'] is True:
		sys.stderr.write('Parameters for subprocess.run:\n')
	#now run the commands
	if len(CmdArr) == 0:
		sys.stderr.write('INFO: No model directory has been found!\n')
	for cmd in CmdArr:
		if dict_Param['DEBUG'] is False:
			while True:
				NumOfIDLsRunning=Taskinfo('.*idl', user=user, RetNumber=True,)
				sys.stderr.write('# of idls running for user '+user+': '+str(NumOfIDLsRunning)+'\n')
				if NumOfIDLsRunning < MaxNumOfTasksToStart:
					break
				else:
					sys.stderr.write('The max # of idl instances ('+str(MaxNumOfTasksToStart)+') for user '+user+' has been reached: '+str(datetime.datetime.now())+'\n')
					sys.stderr.write('Waiting 60s from now to try again\n')
					sleep(60)
				
			sys.stderr.write('Starting: '+' '.join(cmd)+'\n')
			RetVal=subprocess.run(cmd, cwd=dict_Param['ToolDir'], check=True) 
		else:
			sys.stderr.write(','.join([','.join(cmd),'cwd:'+dict_Param['ToolDir']])+'\n')
			#pdb.set_trace()





		

	


