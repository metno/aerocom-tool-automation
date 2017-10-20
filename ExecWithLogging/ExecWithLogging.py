#!/usr/bin/env python3

"""
Start several commands in parallel using the subprocess module.
In addition, gnu screen screen is used to log the output to a text file
and to be able to use the terminal while it is running.

Unfortunately gnu screen does not have a command line switch to tell it
the name of the logfile (it's always called screenlog.X with 
X being the screen session number)
But one can set the log file name in the screenrc file and 
tell screen via the command line to use a certain screenrc file
(-c <file> switch

################################################
Created 20170809 by Jan Griesfeller for Met Norway

Last changed: see github
################################################
"""

import pdb
#import argparse 
import sys
import os
import subprocess
import getpass
#import multiprocessing 
from time import sleep
import datetime
import socket
import re
import itertools


###################################################################################

def GetLogFileName():
	"""
	create a machine dependant log file name for the 
	aerocom-tool-automation module
	"""
	StartTime='{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
	user = getpass.getuser()	
	hostname=socket.gethostname()
	logfile='_'.join([hostname,user,'ExecWithLogging','runlog',StartTime])+'.log'
	logdir='/tmp/'
	if re.search('vis-m',hostname): 
		#then logdir='/lustre/storeB/project/aerocom/logs/runlog/'
		logdir='/lustre/storeA/project/aerocom/logs/runlog/'
	elif re.search('pc4847',hostname):
		logdir='/media/aerocom1/logs/runlog/'
	elif re.search('aerocom-work',hostname):
		logdir='/metno/aerocom/work/logs/runlog/'

	logfile=logdir+logfile

	return logfile

###################################################################################

def ExecWithLogging (*args):
	"""
	execute a shell command line as subprocess using gnu screen
	as middleware to provide logging and the capability to "jump"
	on the command with a shell (using screen -r).

	Since "screen -d" detaches from the terminal directly, it seems for
	the calling python that the command returns immediately while in 
	reality it is still running the the background and logging the command's
	output.

	Unfortunately gnu screen does not have a command line switch to tell it the 
	log file (it's always called screen.<session number>) for the screen 
	session.
	But one can set the log file via .screenrc and tell gnu screen which
	.screenrc file to read via the "-c" command line switch.
	This is what this routine does:
	- write a temporary .screenrc file with a unique log file name
	- start screen telling it the name of the above mentioned .screenrc file
	  and the command to start.
	"""
	import tempfile

	StartTime='{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
	user = getpass.getuser()	
	hostname=socket.gethostname()
	screen='screen'

	logfile=GetLogFileName()

	#create the screenrc file to hand the name of the log file to gnu screen
	OutHandle, screenrcfile=tempfile.mkstemp(suffix='.screenrc', prefix=user+'.', dir='/tmp/', text=False)
	os.write(OutHandle, bytearray(''.join(['logfile ',logfile,'\n']),'utf_8'))
	os.close(OutHandle)
	os.sync()

	sleep(1)
	TempArgs=list(itertools.chain(*args))
	CmdArr=[screen,'-d','-m','-L','-c',screenrcfile,'-S','ExecWithLogging.'+user]+TempArgs
	#pdb.set_trace()
	with open(logfile, 'w') as LogHandle:
		LogHandle.write('screen log file from ExecWithLogging.py started at '+StartTime+'by user '+user+'\n')
		LogHandle.write('argv (separated by "::":\n')
		LogHandle.write('::'.join(TempArgs)+'\n')
		LogHandle.write('Starting command: (separated by "::")'+'\n')
		LogHandle.write('::'.join(CmdArr)+'\n')

	#print(CmdArr,logfile)
	p=subprocess.run(CmdArr)

###############################################################################s##############

def ExecWithPythonLogging(*args):
	"""
	start a command line from python as sub process 
	and log the output to a log file

	Unfortunately using subprocess.PIPE does block the execution.
	Keep this routine for later references and maybe another try 
	to proof the obove sentence wrong.
	"""
	pdb.set_trace()
	StartTime='{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
	user = getpass.getuser()	
	hostname=socket.gethostname()
	screen='screen'

	logfile=GetLogFileName()
	print(logfile)
	
	TempArgs=list(itertools.chain(*args))
	CmdArr=TempArgs
	LogHandle=open(logfile, 'wb')
	LogHandle.write(bytes('log file from ExecWithPythonLogging.py started at '+StartTime+'by user '+user+'\n','utf8'))
	LogHandle.write(bytes('argv (separated by "::":)\n','utf8'))
	LogHandle.write(bytes('::'.join(TempArgs)+'\n','utf8'))
	LogHandle.close()


	#this does not work with multipreocessing :-(
	#with subprocess.Popen(CmdArr, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
		#LogHandle.write(proc.stdout.read())
		#LogHandle.write(proc.stdout.read())

	Output=subprocess.check_output(CmdArr)
	pdb.set_trace()
	#Output=subprocess.check_output(['ls','/home/jang/']+['>>',logfile], shell=True)
	
	LogHandle=open(logfile, 'ab')
	LogHandle.write(bytes('Returncode: '+str(proc.returncode)+'\n','utf8'))

	LogHandle.close()

#############################################################################################

if __name__ == '__main__':
	ExecWithPythonLogging(sys.argv[1:])


