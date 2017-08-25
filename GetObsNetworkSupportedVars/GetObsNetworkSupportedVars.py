#!/usr/bin/env python3

################################################################
# GetObsNetworkSupportedVars.py
#
# program to get the supported variables of an obs network from
#the aerocom-tools
#
# This program is part of the aerocom-tool-automation software
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import sys
import os
import argparse 

def GetObsNetworkSupportedVars(tooldir, ObsNetworkIn, VerboseFlag=False, DebugFlag=False):
	"""
	find the aerocom variables an observation network supports
	by analysing the IDL source file 
	<tooldir>/aerocom_read_include.pro

	This info is needed to rund an entire obs network from the 
	aerocom-tool-automation software.

	Parameters:
		tooldir:			full path to the aerocom-tools directory
		ObsNetworkIn:	String identifying the obs network
							Can be the ones used by the aerocom-tools or those used 
							by aerocom-automation-software

	"""
	###################################################
	#Created 20170824 by Jan Griesfeller for Met Norway
	#
	#last changed: see github
	###################################################
	import re
	import string


	FileToCheck='aerocom_read_include.pro'
	StringToCheck='^c_ObsVarSynonymArr.*,0,0\]'
	StrTest=re.compile(StringToCheck)
	#this is a list of supported obs networks
	ObsnetworkSupported=[]
	ObsnetworkSupported.append('iC_ObsNet_AeronetSun')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSky')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSunNRT')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSunRaw15')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSunRaw20')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSun20AllPoints')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSunV3L15Daily')
	ObsnetworkSupported.append('iC_ObsNet_AeronetSunSDADaily')
	ObsnetworkSupported.append('iC_ObsNet_EBASMultiColumn')
	ObsnetworkSupported.append('iC_ObsNet_AIRBASE')
	ObsnetworkSupported.append('iC_ObsNet_AEROCE')
	ObsnetworkSupported.append('iC_ObsNet_AirbaseEEA')
	ObsnetworkSupported.append('iC_ObsNet_EVAAssim')
	ObsnetworkSupported.append('iC_ObsNet_EVAVal')
	ObsnetworkSupported.append('iC_ObsNet_AeronetForcing')
	ObsnetworkSupported.append('iC_ObsNet_EBASNRT')
	ObsnetworkSupported.append('iC_ObsNet_WOUDCOzoneSonds')

	dict_ToolsObsnetworkName={}
	dict_ToolsObsnetworkName['AERONETSun2.0']='iC_ObsNet_AeronetSunRaw20'
	dict_ToolsObsnetworkName['AERONETSunNRT']='iC_ObsNet_AeronetSunNRT'
	dict_ToolsObsnetworkName['AeronetSunSDADaily']='iC_ObsNet_AeronetSunSDADaily'
	dict_ToolsObsnetworkName['AeronetSunV3L15Daily']='iC_ObsNet_AeronetSunV3L15Daily'
	dict_ToolsObsnetworkName['EAAQeRep']='iC_ObsNet_AirbaseEEA'
	dict_ToolsObsnetworkName['EBASMC']='iC_ObsNet_EBASMultiColumn'

	if ObsNetworkIn in dict_ToolsObsnetworkName:
		ObsNetwork=dict_ToolsObsnetworkName[ObsNetworkIn]
	else:
		ObsNetwork=ObsNetworkIn
	
	if ObsNetwork in ObsnetworkSupported:
		FQFileToCheck=os.path.join(tooldir,FileToCheck)

		if os.path.isfile(FQFileToCheck) is False:
			sys.stderr.write('Error in '+__name__+': file not found: '+FQFileToCheck+').\n')
			sys.exit(2)
		
		#read file
		with open(FQFileToCheck,'r',encoding="latin-1") as InHandle:
			lines=InHandle.readlines()

		VarsSupported=[]

		#Check for variable definition
		for line in lines:
			if StrTest.match(line):
				#print(line)
				#get the index to search for a string like c_ObsVarSynonymArr[9,iC_ObsNet_EBASMultiColumn,0]
				index=line.split('[')[1].split(',')[0].strip()
				aerocomvar1=line.split("'")[1]
				ObsTestStr='c_ObsVarSynonymArr['+index+','+ObsNetwork+',0]='
				#check if var is supoported by current Obsnetwork
				for line2 in lines:
					if ObsTestStr in line2 and (';'+ObsTestStr) not in line2:
						#print(line2)
						VarsSupported.append(aerocomvar1.lower().replace('_',''))
						#pdb.set_trace()

		return VarsSupported
	
	else:
		sys.stderr.write('Error in '+__name__+': obsnetwork not supported: '+ObsNetwork+'\n')
		sys.exit(3)

		return None

###############################################################################

if __name__ == '__main__':
	
	dict_Param={}
	parser = argparse.ArgumentParser(description='GetObsNetworkSupportedVars.py; get variables of an obs network.\n\n')
	parser.add_argument("obsnetname", help="obs network name;")
	parser.add_argument("--tooldir", help="set the directory of the aerocom-tools; if unset ${HOME}/aerocom-tools/ will be used")
	parser.add_argument("-v","--verbose", help="switch on verbosity",action='store_true')
	parser.add_argument("--debug", help="switch on debug mode: Do NOT start idl, just print what would be done",action='store_true')
	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.obsnetname:
		dict_Param['ObsName']=args.obsnetname

	if args.debug:
		dict_Param['DEBUG']=args.debug
	else:
		dict_Param['DEBUG']=False

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
	
	VarsSupported=GetObsNetworkSupportedVars(dict_Param['ToolDir'], dict_Param['ObsName'], dict_Param['VERBOSE'], dict_Param['DEBUG'])
	#pdb.set_trace()
	print(','.join(VarsSupported))
