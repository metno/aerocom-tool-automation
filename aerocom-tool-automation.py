#!/usr/bin/env python3

################################################################
# aerocom-tool-automation.py
#
# main program of the aerocom-tool-automation software
# 
# The purpose of this program is to plot all possible plots of a new 
# model version
# At first we will need a model directory as parameter, but 
# the ultimate goal is to just need the model name
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


def Taskinfo(Name, user=False, PrintInfo=False, RetNumber=False, VerboseFlag=False, DebugFlag=False):
	#procedure to imitate ps -ef | grep <progname> using the psutil package
	import psutil, re

	RetVal=[]

	Regexp = re.compile(Name, re.IGNORECASE)
	if user is not False:
		UserRegexp = re.compile(user)
	for proc in psutil.process_iter():
		try:
			pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline','username'])
		except psutil.NoSuchProcess:
			pass
		else:
			if Regexp.match(pinfo['name']):
				if user is not False:
					if UserRegexp.match(pinfo['username']):
						RetVal.append(pinfo)
				else:
					RetVal.append(pinfo)


	if PrintInfo:
		print(RetVal)

	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	if RetNumber:
		return len(RetVal)

	return RetVal



if __name__ == '__main__':
	
	dict_Param={}
	parser = argparse.ArgumentParser(description='aerocom-automation-tools\nProgram to automate aerocom-tool plotting based on just the model name\n\n')
	parser.add_argument("model", help="model names to use; can be a comma separated list;")
	parser.add_argument("--obsyear", help="observation years to run; use 9999 for climatology, leave out for same as model year")
	parser.add_argument("--tooldir", help="set the directory of the aerocom-tools; if unset ${HOME}/aerocom-tools/ will be used")
	parser.add_argument("--nosend", help="switch off webserver upload",action='store_true')
	#parser.add_argument("-p","--print", help="switch on idl include file name printing to stdout. Might be useful for external programs",action='store_true')
	parser.add_argument("-v","--verbose", help="switch on verbosity",action='store_true')
	parser.add_argument("--script", help="script to start; defaults to <tooldir>/StartScreenWithLogging.sh")
	parser.add_argument("--debug", help="switch on debug mode: Do NOT start idl, just print what would be done",action='store_true')
	parser.add_argument("--numcpu", help="Number of Processes to start. Default is using half of the number of logical cores available.",type=int)
	parser.add_argument("--idl", help="location of the idl binary. Uses $IDL_DIR/bin/idl as default")

	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.idl:
		dict_Param['IDL']=args.idl
	else:
		dict_Param['IDL']='/modules/xenial/user-apps/aerocom-IDL/8.5.1/idl85/bin/idl'
		dict_Param['IDL']=os.path.join(os.environ['IDL_DIR'],'bin','idl')
		if os.path.isfile(dict_Param['IDL']) is False:
			sys.stderr.write('Error: idl not found!\n')
			sys.stderr.write('Path: '+dict_Param['IDL']+'\n')
			sys.stderr.write('Please supply the correct location with the --idl switch\n')

	if args.numcpu:
		dict_Param['NumCPU']=args.numcpu

	if args.model:
		dict_Param['ModelName']=args.model.split(',')

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
		dict_Param['ToolDir']=os.path.join(os.environ['HOME'],'data','aerocom-tools')
	
	if args.script:
		dict_Param['SCRIPT']=args.script
	else:
		#dict_Param['SCRIPT']=os.path.join(dict_Param['ToolDir'],'StartBatchParam_MT_log.sh')
		dict_Param['SCRIPT']=os.path.join(dict_Param['ToolDir'],'StartScreenWithLogging.sh')

	if args.obsyear:
		dict_Param['ObsYear']=args.obsyear
	else:
		dict_Param['ObsYear']='0000'


	MaxTimeDiffDays=2.
	

	#get the folder the data is located in for each model
	#non existing models are ignored and there will be no error
	#message unless one model is present
	#returns a list
	ModelFolders=GetModelDir.GetModelDir(dict_Param['ModelName'],
		c_ConfigFile='./folders.ini', VerboseFlag=False)

	#get the supported variables list
	dict_SupportStruct=WriteIDLIncludeFile.GetIDLIncludeFileText('nogroup','whatever', all=True)
	SupportedVars=','.join(sorted(dict_SupportStruct['VARS'].keys()))
	CmdArr=[]
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
			#if Var in ['ps']: 
			#continue	#no idea why 'ps' in SupportedVars returns True
			try:
				Dummy=dict_SupportStruct['VARS'][Var]
			except KeyError:
				if dict_Param['VERBOSE'] == True:
					sys.stderr.write('WARNING: Variable "'+Var+'" not supported by the aerocom-automation-tools\n')
					sys.stderr.write('Continuing with the other variables.\n')
				continue

			#if Var not in SupportedVars:
				#if dict_Param['VERBOSE'] == True:
					#sys.stderr.write('WARNING: Variable "'+Var+'" not supported by the aerocom-automation-tools\n')
					#sys.stderr.write('Continuing with the other variables.\n')
				#continue
				
			#now write the include file
			#one per variable
			dict_Param['IDLOutFile']=os.path.join(dict_Param['ToolDir'],'batching',Model+'_'+Var+'_include.pro')
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

			#if len(Years) > 0:
			for Year in Years:
				if dict_Param['VERBOSE'] == True:
					sys.stderr.write('Year: '+Year+'\n')

				#Create an array with program calls for IDL

				#cmd=[dict_Param['SCRIPT'],dict_Param['IDLOutFile'], ModellistFile]

				#pdb.set_trace()
				OutFile, IncFile=ModAerocomMain.ModAerocomMain(dict_Param['ToolDir'], dict_Param['IDLOutFile'])
				#IDL does not like the filename ending with '.pro', so remove that
				OutFile=OutFile.replace('.pro','')
				IdlCmd=OutFile+",modelin=['"+Model+"'],yearin=['"+Year+"'],datayearin='"+dict_Param['ObsYear']+"'"
				SessionName='_'.join([Model,Var,Year])
				cmd=['/bin/bash',dict_Param['SCRIPT'], '-d', '-L', '-m', '-S', SessionName, dict_Param['IDL'], '-queue', '-e' , IdlCmd]
				#cmd=[dict_Param['SCRIPT'], '-d', '-L', '-m', dict_Param['IDL'], '-queue', '-e' , IdlCmd]
				CmdArr.append(cmd)



	
	user = getpass.getuser()
	try:
		MaxNumOfTasksToStart=dict_Param['NumCPU']
	except KeyError: 
		MaxNumOfTasksToStart=multiprocessing.cpu_count()/2

	taskinfo=Taskinfo('.*idl', user=user, RetNumber=True,)

	if dict_Param['DEBUG'] is True:
		sys.stderr.write('Parameters for subprocess.run:\n')
	#now run the commands
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
			pdb.set_trace()





		

	


