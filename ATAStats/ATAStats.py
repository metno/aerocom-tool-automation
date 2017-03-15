#!/usr/bin/env python3

################################################################
# ATAStats.py
#
# Program to analyse the runlogs created by the aerocom idl tools
#################################################################
# Created 20170315 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import os
import glob
import argparse 
import sys
import getpass
import re
import math
import shutil

def ATAStats(RunLogDir, MoveSuccessLogs=False, DeleteSuccessLogs=False, DoNothingFlag=False, VerboseFlag=False, 
	AllUserFlag=False, DebugFlag=False):
	#procedure to analyse the log files of the idl aerocom tools
	# get a list of files
	if os.path.isdir(RunLogDir):
		OutData={}
		VarOutData={}
		ModelOutData={}
		i_ModelPos=1
		i_ModelYearPos=3
		i_DataYearPos=5
		SuccessDir=os.path.join(RunLogDir,'success')
		try:
			os.mkdir(SuccessDir)
		except FileExistsError:
			pass
		if AllUserFlag is False:
			logfiles=glob.glob(os.path.join(RunLogDir,'*'+getpass.getuser()+'*.log'))
		else:
			logfiles=glob.glob(os.path.join(RunLogDir,'*.log'))
		for logfile in logfiles:
			#Leave out size 0 files
			if os.path.getsize(logfile) == 0:
				if VerboseFlag is True:
					sys.stderr.write(logfile+' has zero length. Skipping\n')
				continue
			LogName=os.path.basename(logfile)
			OutData[LogName]={}
			if VerboseFlag is True:
				sys.stderr.write('reading: '+logfile+'\n')
			with open(logfile, 'rt') as InFile:
				FileData=InFile.readlines()
			#pdb.set_trace()
			#now start the analysis and put the data into the OutData dict
			#line 10 is written to the log even when idl failed to start
			#so we should be able to rely on it
			#UNFORTUNATELY this is not the case
			for line in FileData:
				if 'aerocom_main_' in line:
					c_DummyArr=line.split("'")
					break

			OutData[LogName]['Model']=c_DummyArr[i_ModelPos]
			OutData[LogName]['ModelYear']=c_DummyArr[i_ModelYearPos]
			OutData[LogName]['ObsYear']=c_DummyArr[i_DataYearPos]
			if '0000' in OutData[LogName]['ObsYear']: OutData[LogName]['ObsYear'] = OutData[LogName]['ModelYear']

			#test if the job ran through without problems
			#if yes, don't do a deeper analysis for now
			OutData[LogName]['Success']=False
			OutData[LogName]['LastLines']=FileData[-10:-1]
			OutData[LogName]['CHECK']=[]
			OutData[LogName]['MeanValOrig']=[]
			OutData[LogName]['ModelDir']=''
			OutData[LogName]['Var']=''
			OutData[LogName]['Halted']=[]
			OutData[LogName]['ModelFileName']=''
			if 'total size' in FileData[-1]:
				#assume that the job ran without problems for now if some plots were transfered
				OutData[LogName]['Success']=True
				#test if the logs for successfully run jobs should be moved or deleted
				if MoveSuccessLogs is True:
					#Move file to success directory
					if VerboseFlag is True:
						if DoNothingFlag is False:
							sys.stderr.write(logfile+' moved to success directory\n')
						else:
							sys.stderr.write(logfile+' would have been moved to success directory\n')
							
					if DoNothingFlag is False:
						shutil.move(logfile, SuccessDir)
				elif DeleteSuccessLogs is True:
					#delete logs of successful run jobs
					if VerboseFlag is True:
						if DoNothingFlag is False:
							sys.stderr.write(logfile+' deleted\n')
						else:
							sys.stderr.write(logfile+' would have been deleted\n')
					if DoNothingFlag is False:
						os.remove(logfile)
				#continue
			

			#Now search for some stuff
			for line in FileData:
				if 'ABOUT TO READ MODELS' in line:
					#ABOUT TO READ MODELS /lustre/storeB/project/aerocom/aerocom-users-database/AEROCOM-PHASE-II/GOCART-v4.A2.PRE/renamed/
					OutData[LogName]['ModelDir']=line.split()[4]
					continue
				if 'Searched:' in line:
					#Searched: DRY_SO4 => VarInFile:  DRYSO4 / All vars to Read DRY_SO4
					OutData[LogName]['Var']=line.split()[1]
					continue
				if 'Reading file:' in line:
					#Reading file: aerocom.GOCART-v4.A2.PRE.daily.dryso4.2006.nc
					OutData[LogName]['ModelFileName']=line.split()[2]
					continue
				if 'CHECK:' in line:
					#CHECK: Warning Model GOCART_V4_A2_PRE Var DRY_SO4 not properly read
					OutData[LogName]['CHECK'].append(line.strip())
					continue
				if 'mean original value' in line:
					OutData[LogName]['MeanValOrig'].append(line.split()[-1])
					continue
				if '% Execution halted' in line:
					OutData[LogName]['Halted'].append(line)
					continue

			#pdb.set_trace()

			#Now build a model sorted list of file names
			try:
				ModelOutData[OutData[LogName]['Model']].append(LogName)
			except KeyError:
				ModelOutData[OutData[LogName]['Model']]=[]
				ModelOutData[OutData[LogName]['Model']].append(LogName)

	else:
		sys.stderr.write("ERROR: input directory "+RunLogDir+" not found!\n")
		os.exit(1)

	if DebugFlag:
		pdb.set_trace()

	return OutData, ModelOutData

##########################################################################################

def PrintAtaStats(InData,ModelInData,FailedOnlyFlag=False):
	#procedure to pretty print the ATAStats output struct
	#for key in InData:
		#pdb.set_trace()
		#sys.stdout.write('|'.join([key,InData[key]['Var'], InData[key]['ModelYear'], InData[key]['ObsYear'],InData[key]['Model']]))
		#sys.stdout.write("\n")

	MaxModelStrLength=25
	MaxYearLength=4
	MaxVarLength=12
	#Print a list of successful and failed jobs sorted by model name and variable
	PrintDataFail={}
	PrintDataSuccess={}
	for Model in sorted(ModelInData):
		#pdb.set_trace()
		for key in ModelInData[Model]:
			PrintKey='.'.join([Model,InData[key]['Var']])
			if InData[key]['Success'] is True:
				PrintDataSuccess[PrintKey]=(' | '.join([InData[key]['Model'].ljust(MaxModelStrLength),InData[key]['Var'].ljust(MaxVarLength), 
					InData[key]['ModelYear'].ljust(MaxYearLength), InData[key]['ObsYear'].ljust(MaxYearLength+3),key]))
			else:
				PrintDataFail[PrintKey]=(' | '.join([InData[key]['Model'].ljust(MaxModelStrLength),InData[key]['Var'].ljust(MaxVarLength), 
					InData[key]['ModelYear'].ljust(MaxYearLength), InData[key]['ObsYear'].ljust(MaxYearLength+3),key]))
				#work on the reasons for failure
				try:
					MeanVal=float(InData[key]['MeanValOrig'][0])
					if math.isnan(MeanVal) is True or MeanVal == 0.:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],'MeanVal = '+InData[key]['MeanValOrig'][0]])
					elif len(InData[key]['Halted']) > 0:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],InData[key]['Halted'][0]])
					elif len(InData[key]['CHECK']) > 0:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],InData[key]['CHECK'][0]])
				except IndexError:
					if len(InData[key]['Halted']) > 0:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],InData[key]['Halted'][0]])
					elif len(InData[key]['CHECK']) > 0:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],InData[key]['CHECK'][0]])
					else:
						PrintDataFail[PrintKey]=' | '.join([PrintDataFail[PrintKey],'Unknown'])
					pass
					

	if FailedOnlyFlag is False:
		sys.stdout.write("Success:\n")
		sys.stdout.write(' | '.join(['Model'.ljust(MaxModelStrLength),'Var'.ljust(MaxVarLength),
			'Year'.ljust(MaxYearLength),'ObsYear'.ljust(MaxYearLength),'log file name'])+'\n')
		for line in sorted(PrintDataSuccess):
			sys.stdout.write(PrintDataSuccess[line])
			sys.stdout.write("\n")

	sys.stdout.write("Failed:\n")
	sys.stdout.write(' | '.join(['Model'.ljust(MaxModelStrLength),'Var'.ljust(MaxVarLength),
		'Year'.ljust(MaxYearLength),'ObsYear'.ljust(MaxYearLength),'log file name','Reason'])+'\n')
	for line in sorted(PrintDataFail):
		sys.stdout.write(PrintDataFail[line])
		
		sys.stdout.write("\n")

##########################################################################################

if __name__ == '__main__':

	dict_Param={}
	parser = argparse.ArgumentParser(description='ATAStats: Program to analyse run logs of the aerocom-tool-automation software\n\n',)
	#epilog='RI#eturns some general statistics')
	parser.add_argument("-d","--directory", help="use directory. Defaults to /lustre/storeB/project/aerocom/logs/runlog", default='/lustre/storeB/project/aerocom/logs/runlog')
	parser.add_argument("-m","--movelogs", help="move successfully run log files to <success directory>", action='store_true')
	parser.add_argument("--deletelogs", help="delete successfully run log files", action='store_true')
	parser.add_argument("-f","--failedonly", help="list only failed jobs", action='store_true')
	parser.add_argument("-n","--donothing", help="do nothing, just print, what would be done", action='store_true')
	parser.add_argument("-v","--verbose", help="be verbose", action='store_true')
	parser.add_argument("-a","--allusers", help="analyse all logfiles, not just your own", action='store_true')
	#parser.add_argument("-l", help="")

	args = parser.parse_args()

	if args.allusers:
		dict_Param['allusers']=args.allusers
	else:
		dict_Param['allusers']=False

	if args.verbose:
		dict_Param['verbose']=args.verbose
	else:
		dict_Param['verbose']=False

	if args.donothing:
		dict_Param['donothing']=args.donothing
	else:
		dict_Param['donothing']=False

	if args.failedonly:
		dict_Param['failedonly']=args.failedonly
	else:
		dict_Param['failedonly']=False

	if args.movelogs:
		dict_Param['movelogs']=args.movelogs
	else:
		dict_Param['movelogs']=False
	
	if args.deletelogs:
		dict_Param['deletelogs']=args.deletelogs
	else:
		dict_Param['deletelogs']=False


	if args.directory:
		dict_Param['dir']=args.directory
	else:
		dict_Param['dir']='/lustre/storeB/project/aerocom/logs/runlog'

	if os.path.isdir(dict_Param['dir']) is False:
		sys.stderr.write('Error: The supplied directory does not exist. Exiting.\n')
		sys.exit(1)
		
	#pdb.set_trace()
	ATAStatData, ModelATAStatData=ATAStats(dict_Param['dir'], DoNothingFlag=dict_Param['donothing'], 
		AllUserFlag=dict_Param['allusers'], MoveSuccessLogs=dict_Param['movelogs'], 
		DeleteSuccessLogs=dict_Param['deletelogs'], VerboseFlag=dict_Param['verbose'], DebugFlag=False)
	PrintAtaStats(ATAStatData, ModelATAStatData, FailedOnlyFlag=dict_Param['failedonly'])

