#!/usr/bin/env python3

################################################################
# ModAerocomMain.py
#
# program to make the main program of aerocom-tools aerocom_main.pro
# fit for multiprocessor usage, by renaming the file, the program name and
# the include file to a unique one 
# Replacement for the shell script 
# Aerocom_PrepAerocomMain.sh 
# https://github.com/metno/aerocom-tools/blob/master/Aerocom_PrepAerocomMain.sh
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import os
import argparse
import sys
import uuid
import socket

def ModAerocomMain(Path, IncFile, VerboseFlag=False, DebugFlag=False):
	if DebugFlag:
		pdb.set_trace()
	if os.path.isdir(Path):
		FileName=os.path.join(Path,'aerocom_main.pro')
		OutIncFile=''
		OutFile=''
		if os.path.isfile(FileName):
			with open(FileName) as FHandle:
				FileString=FHandle.read()
			#create a uuid and append the host name for easier removal later on
			UUID='_'.join([str(uuid.uuid4()),socket.gethostname()]).replace('-','_')
			#New procedure name
			NewMainStr='aerocom_main_'+UUID
			NewMainFile=NewMainStr+'.pro'
			#New include file name
			NewIncStr='IDL_includetemp_'+UUID
			NewIncFile=NewIncStr+'.pro'
			FileString=FileString.replace('aerocom_main',NewMainStr)
			FileString=FileString.replace('IDL_includetemp',NewIncStr)
			OutFile=FileName.replace('aerocom_main',NewMainStr)
			with open(OutFile,'w') as FHandle:
				FHandle.write(FileString)
				FHandle.flush()
				os.fsync(FHandle.fileno())


			#now link the include file to the target
			os.chdir(Path)
			os.symlink(IncFile, NewIncFile)
		else:
			sys.stderr.write("Error: file not found: "+FileName+" \n")
			sys.stderr.write('Exiting.\n')
			sys.exit(2)

	else:
		sys.stderr.write("Error: path does not exist: \n")
		sys.stderr.write('Exiting.\n')
		sys.exit(1)


	if VerboseFlag:
		print(OutFile)
	if DebugFlag:
		pdb.set_trace()

	OutFile=os.path.basename(OutFile)

	return OutFile, NewIncFile


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='''
	Modify the aerocom-tool's aerocom_main.pro to a unique program name that is safe to use in a multiprocessing environment.
	The way ths works is that aerocom-main.pro is extended with a UUID that is then used to rename the main procedure, the 
	the file name and for a unique link to the include file.
	Returns the file/link created relative to the directory given in aerocomdir.
	''')
	#parser.add_argument("mainfile", help="aerocom main filename to use as template")
	parser.add_argument("aerocomdir", help="directory of the aerocom-tools (location of aerocom_main.pro)")
	parser.add_argument("incfile", help="include file to link RELATIVE to aerocomdir, or with absolute path")
	#parser.add_argument("incfile", help="IDL include file to use as template")
	parser.add_argument("-c","--commasep", help="return get a comma separated list",action='store_true')
	args = parser.parse_args()
	try:
		OutFile, OutIncFile=ModAerocomMain(args.aerocomdir, args.incfile, VerboseFlag=False, DebugFlag=False)
	except:
		#this will never be called since we need only mandantory arguments
		pass

	try:
		if args.commasep:
			sys.stdout.write(','.join([OutFile,OutIncFile])+'\n')
		else:
			sys.stdout.write('\n'.join([OutFile,OutIncFile])+'\n')
	except NameError:
		sys.exit(1)

