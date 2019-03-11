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
import GetObsNetworkSupportedVars


###################################################################################


if __name__ == '__main__':
	import configparser
	max_year = 2019

	#get all supported obs networks to use that in the text
	dict_SupportStruct=WriteIDLIncludeFile.GetIDLIncludeFileText('nogroup','whatever', all=True)
	SupportedObsNetworks=', '.join(sorted(dict_SupportStruct['OBSNETWORKS'].keys()))

	#Read Ini file for some parameters
	ConfigIni=os.path.join(os.path.dirname(os.path.realpath(__file__)),'constants.ini')
	IniFileData=configparser.ConfigParser()
	IniFileData.read(ConfigIni)
	ObsOnlyModelName=IniFileData['parameters']['ObsOnlyModelname']

	#set default location of the aerocom-idl directory
	#1st we look at the environment variable AEROCOMWORKDIR,
	try:
		ToolDir = os.environ['AEROCOMWORKDIR']
	except KeyError:
		ToolDir = None

	#then we check for ${HOME}/aerocom-idl
	if ToolDir is None:
		ToolDir = os.path.join(os.environ['HOME'],'aerocom-tools')
		
	#check if ToolDir exist. If not, delete variable
	if not os.path.isdir(ToolDir):
		ToolDir = None
		
	user = None
	user = getpass.getuser()

	default_num_cpu = 4

	#command line interface using argparse
	dict_Param={}
	parser = argparse.ArgumentParser(description='aerocom-automation-tools\nProgram to automate aerocom-tool plotting based on just the model name\n\n')
	parser.add_argument("model", help="model names to use; can be a comma separated list;use "+ObsOnlyModelName+" for observations only")
	parser.add_argument("--variable", help="Run only a list of variables. List has to be comma seperated.")
	parser.add_argument("--modelyear", help="model years to run; use 9999 for climatology, leave out for all years; comma separated list; Use this to limit the plotting of the OBSERVATION-ONLY model to certain years.")
	parser.add_argument("--obsyear", help="observation years to run; use 9999 for climatology, leave out for same as model year")
	if ToolDir is None:
		parser.add_argument("--tooldir", help="set the directory of the aerocom-tools; WARNING no tool dir found. Please provide one!")
	else:
		parser.add_argument("--tooldir", help="set the directory of the aerocom-tools; if unset "+ToolDir+" will be used")
	parser.add_argument("--nosend", help="switch off webserver upload",action='store_true')
	parser.add_argument("-p","--print", help="switch on idl include file name printing to stdout. Might be useful for external programs",action='store_true')
	parser.add_argument("-v","--verbose", help="switch on verbosity",action='store_true')
	parser.add_argument("--script", help="script to start; defaults to <tooldir>/StartScreenWithLogging.sh")
	parser.add_argument("--debug", help="switch on debug mode: Do NOT start idl, just print what would be done",action='store_true')
	parser.add_argument("--numcpu", help="Number of Processes to start. Default is using {}.".format(default_num_cpu),type=int,default=default_num_cpu)
	parser.add_argument("--idl", help="location of the idl binary. Uses $IDL_DIR/bin/idl as default")

	parser.add_argument("--outputdir", help="directory where the idl include files will be put. Default is <tooldir>/batching/<user name>. Directory needs to exist.")
	parser.add_argument("--obsnetwork", help="OBERVATIONS-ONLY mode: run all variables for a certain obs network; model mode: Run a variable with a non standard obs network. Supported are "+SupportedObsNetworks)
	parser.add_argument("--forecast", help="forecast mode for CAMS; daily maps only, nothing else",action='store_true')
	parser.add_argument("--htapfilters", help="also run the htap filters; model has to have 1x1 degree resolution at the moment",action='store_true')
	parser.add_argument("--htapfiltersonly", help="only include the HTAP pixel based filters",action='store_true')
	parser.add_argument("--aodtrends", help="run the AODTREND filters AODTREND95TO12,AODTREND,AODTREND95",action='store_true')
	parser.add_argument("--plotdailyts", help="also plot daily time series",action='store_true')
	parser.add_argument("--addsubvars", help="add sub variables; works only for the variable od550aer atm.",action='store_true')
	parser.add_argument("--notimeseries", help="switch off time series plotting",action='store_true')
	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.numcpu:
		dict_Param['NumCPU']=args.numcpu

	if args.variable:
		dict_Param['VariablesToRun']=args.variable.split(',')
		#now build a dict with var as key, and the 'real var name as value
		#used to make special variable model possible
		#e.g. od550aer_Forecast
		dict_Vars={}
		for Var in dict_Param['VariablesToRun']:
			if Var in IniFileData['VariableAliases']:
				dict_Vars[Var]=IniFileData['VariableAliases'][Var]
			else:
				dict_Vars[Var]=Var

	if args.model:
		dict_Param['ModelName']=args.model.split(',')

	if args.htapfilters:
		dict_Param['HTAPFILTERS']=args.htapfilters

	if args.aodtrends:
		dict_Param['AODTRENDS']=args.aodtrends

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
		if ToolDir is None:
			sys.stderr.write('Error: aerocom-tool directory not found in any of the default locations!\n')
			sys.stderr.write('($AEROCOMWORKDIR or ${HOME}/aerocom-tools). Please supply the location of \n')
			sys.stderr.write('the aerocom-tools using the --tooldir switch. \n')
			sys.exit(2)
		else:
			dict_Param['ToolDir']=ToolDir
	
	if not os.path.isdir(dict_Param['ToolDir']):
		sys.stderr.write('Error: supplied tool dir '+dict_Param['ToolDir']+' does not exist. Exiting\n')
		sys.exit(1)

	if args.verbose:
		sys.stderr.write('using tooldir '+dict_Param['ToolDir']+'\n')
	
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
		dict_Param['OutputDir']=os.path.join(dict_Param['ToolDir'],'batching',user)

	#create user specific batching directory
	try:
		os.mkdir(dict_Param['OutputDir'])
	except FileExistsError:
		pass

	if args.obsnetwork:
		dict_Param['ObsnetworksToRun']=args.obsnetwork.split(',')
		#use the 1st for model plotting for now
		dict_Param['ObsNetworkName']=args.obsnetwork.split(',')

	if args.forecast:
		dict_Param['FORECAST']=args.forecast

	if args.plotdailyts:
		dict_Param['PLOTDAILYTIMESERIES']=args.plotdailyts

	if args.addsubvars:
		dict_Param['ADDSUBVARS']=args.addsubvars

	if args.notimeseries:
		dict_Param['NOTIMESERIES']=args.notimeseries

	if args.htapfiltersonly:
		dict_Param['HTAPFILTERSONLY']=args.htapfiltersonly



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
					ModellistFile=os.path.join(dict_Param['OutputDir'], ObsNetWork+'_'+Var+'.txt')
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
					Years=list(map(str,range(ObsStartYear,max_year)))

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
		#pdb.set_trace()
		for Model in ModelFolders:
			#just the 1st model dir for now
			Modeldir=os.path.join(ModelFolders[Model][0],'renamed')
			VarsInModel=GetModelVars.GetModelVars(Modeldir)
			if args.variable:
				VarsToRun=dict_Vars.values()
			else:
				VarsToRun=VarsInModel
				
			if dict_Param['VERBOSE'] is True:
				sys.stderr.write('Modeldir: '+Modeldir+'\n')
			#loop through the Variables an determine the years they are present
			for Var in VarsToRun:
				try:
					Dummy=dict_SupportStruct['VARS'][Var]
				except KeyError:
					if dict_Param['VERBOSE'] is True:
						sys.stderr.write('WARNING: Variable "'+Var+'" not supported by the aerocom-automation-tools\n')
						sys.stderr.write('Continuing with the other variables.\n')
					continue

				#loop through the obsnetworks if these were set by the command line
				if args.obsnetwork:
					if len(dict_Param['ObsnetworksToRun']) > 1:
						sys.stderr.write('ERROR: running several user defined obs networks at once is not yet supported.\n')
						sys.stderr.write('Please run them using several commands at this point and contact jang to get\n')
						sys.stderr.write('this feature implemented. Exiting now.\n')
						sys.exit(4)
						
					for ObsNetWork in dict_Param['ObsnetworksToRun']:
						#determine variables
						dict_Param['ObsNetworkName']=ObsNetWork
						#now write the idl include file
						#one per variable
						dict_Param['IDLOutFile']=os.path.join(dict_Param['OutputDir'],Model+'_'+Var+'_'+ObsNetWork+'_include.pro')
						dict_Param['VarName']=Var
						#Maybe we want to check if the variable is actually supported
						#ModellistFile=os.path.join(dict_Param['ToolDir'],'batching', Model+'_'+Var+'.txt')
						ModellistFile=os.path.join(dict_Param['OutputDir'], Model+'_'+Var+'.txt')
						#write IDL include file
						try:
							WriteIDLIncludeFile.WriteIDLIncludeFile(dict_Param)
						except SystemExit:
							pass
				else:
					#now write the idl include file
					#one per variable
					dict_Param['IDLOutFile']=os.path.join(dict_Param['OutputDir'],Model+'_'+Var+'_include.pro')
					dict_Param['VarName']=Var
					#Maybe we want to check if the variable is actually supported
					#ModellistFile=os.path.join(dict_Param['ToolDir'],'batching', Model+'_'+Var+'.txt')
					ModellistFile=os.path.join(dict_Param['OutputDir'], Model+'_'+Var+'.txt')
					#write IDL include file
					try:
						WriteIDLIncludeFile.WriteIDLIncludeFile(dict_Param)
					except SystemExit:
						pass

				#For the include file we have some 'pseudo variables' for special purposes like the
				#dust forecast.
				#The real variable name is actually everything before the underscore

				Var=Var.split('_')[0]
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
	try:
		MaxNumOfTasksToStart=dict_Param['NumCPU']
	except KeyError: 
		MaxNumOfTasksToStart=multiprocessing.cpu_count()/2

	taskinfo=Taskinfo('.*idl', user=user, RetNumber=True,)

	if dict_Param['DEBUG'] is True:
		sys.stderr.write('Parameters for subprocess.run:\n')
	#now run the commands
	if len(CmdArr) == 0:
		sys.stderr.write('INFO: No commands to run! Wrong variable name?\n')
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





		

	


