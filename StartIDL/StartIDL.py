#!/usr/bin/env python3

################################################################
# WriteIDLIncludeFile.py
#
# program to write an IDL include file for a given aerocom
# variable
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
from multiprocessing import Process


def GetIDLLoc( VerboseFlag=False, DebugFlag=False):
	#function to return the location of the idl binary
	#
	#the value is taken from the environment variable 'IDL_DIR' set
	#by the standard idl installation 
	# OR
	#fall back to "/usr/local/bin/idl" if the first is not present
	#(works e.g. at a local installation)

	import os

	IDLDir=os.environ['IDL_DIR']
	if IDLDir == None:
		RetVal='/usr/local/bin/idl'
	else:
		RetVal=IDLDir+'/bin/idl'
	
	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	return RetVal



def StartIDLSingleThread(MainProg, IDL=None, WorkDir=None, IncFile=None, VerboseFlag=False, DebugFlag=False):
	#this is running idl single threaded, and is waiting for the 
	#sub process to finish
	#Then the object from subprocess.run is returned
	
	import subprocess
	import os

	if IDL == None: 
		IDL=GetIDLLoc()

	if VerboseFlag:
		print('IDL:',IDL)

	RetVal=subprocess.run(['screen', '-d', '-L', '-m', IDL,
		'-e', MainProg],
		cwd=WorkDir, 
		check=True, 
		stdout=subprocess.PIPE, 
		stderr=subprocess.PIPE)

	#RetVal['ParentPID']=os.getppid()
	#RetVal['PID']=os.getpid()

	if VerboseFlag:
		print(RetVal.stdout)
	if DebugFlag:
		pdb.set_trace()

	return RetVal

##############################################################

def StartIDLMultiThreaded(MainProg, WorkDir=None, IncFile=None, 
	VerboseFlag=False, DebugFlag=False):

	#this will start idl multitreaded with the indicated # of instances
	#at once
	#once all idl instances have finished, their output is returned

	import multiprocessing

	IDL=GetIDLLoc()
	if VerboseFlag:
		print('IDL:',IDL)

	count = multiprocessing.cpu_count()
	#pool = multiprocessing.Pool(processes=count)
	RetData=[]
	#print pool.map(StartIDLSingleThread, MainProg, IDL, WorkDir=WorkDir, )
	#pool.apply_async(StartIDLSingleThread, MainProg[0], IDL, WorkDir=WorkDir, RetVal.append())
	keywords={'WorkDir':WorkDir,'VerboseFlag':False,'DebugFlag':False}


	Pool=multiprocessing.Pool(processes=4)
	for Cmd in MainProg:
		#process = multiprocessing.Process(target=StartIDLSingleThread, args=(Cmd,IDL,),
			#kwargs=keywords)
		#process.start()
		result = Pool.apply_async(StartIDLSingleThread, (Cmd,IDL,), keywords)
		RetData.append(result)

	

	if DebugFlag:
		pdb.set_trace()
	

	if VerboseFlag:
		print(RetVal.stdout)
	if DebugFlag:
		pdb.set_trace()

	return RetVal



if __name__ == '__main__':
	#MainProg='/home/jang/data/aerocom-tools/aerocom_main_testing'
	#MainProg='aerocom_main_testing'
	MainProg=[]
	MainProg.append('aerocom_main_testing')
	MainProg.append('aerocom_main_testing_2')

	cwd='/home/jang/data/aerocom-tools' 
	#IDLParameters=",modelin=[\'OBSERVATIONS-ONLY\'],yearin=[\'2012\'],datayearin=[\'0000\']"
	#IDLParameters=",modelin=[\'OBSERVATIONS-ONLY\']"
	IDLParameters=[]
	IDLParameters.append(",modelin=[\'OBSERVATIONS-ONLY\']")
	IDLParameters.append(",modelin=[\'OBSERVATIONS-ONLY_2\']")

	MainProg=[MainProg[x]+IDLParameters[x] for x in range(0,2)]

	
	#RetVal=StartIDLSingleThread(MainProg+IDLParameters, WorkDir=cwd, VerboseFlag=True)
	RetVal=[]
	RetVal=StartIDLMultiThreaded(MainProg, WorkDir=cwd, VerboseFlag=True, 
		DebugFlag=True)
	#print(RetVal)

