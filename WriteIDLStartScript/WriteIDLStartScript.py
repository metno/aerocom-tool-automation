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
imp


def WriteIDLStartScript(OutFile, VerboseFlag=False, DebugFlag=False):
	
	CommonStart="""
#!/bin/bash
# to set AEROCOMWORKDIR put in .cshrc a line like this: setenv AEROCOMWORKDIR '/home/aerocom0/IDL/AEROCOMLIB'
c_TestDummy=`env | grep -c AEROCOMWORKDIR`
if [ "$c_TestDummy" == "1" ] ; then 
	cd $AEROCOMWORKDIR
	pwd
else 
	echo environment variabe AEROCOMWORKDIR not found! Batching does not work without that environment variable
	exit 1
fi
# List of possible model sets (edited in ./modellists); with model years
#set -A mlist emepReporting2011
mlist=('observations-only_since_1995')

# List of possible include files
#set -A ilist OD550_AER ANG4487_AER OD550GT1_AER SCONC_PM10 ABS550_AER OD550LT1_AER WET_SO4 SCONC_SO4 SCONC_SO2 DEP_DUST SCONC_DUST  maps mapsfluxes budgets SCATC550DRY_AER ABSC550DRY_AER VM3_O3 SCONC_BC forcingmaps


#set -A ilist OD550_AER_CCI2000
ilist=('OD550_AER_ONLY_AeronetSun2.0-ObsOnly')
#set -A ilist OD550_AER_CCI OD550LT1_AER OD550GT1_AER OD865_AER ANG4487_AER OD550ERR_AER

for il in ${ilist[*]} ; do
file=${AEROCOMWORKDIR}/include/mic_include_${il}.pro
if  [ -f  $file ] ; then
${AEROCOMWORKDIR}/StartBatchParam_MT.sh $file ${mlist[*]}
fi 
done

	"""
	RetVal=GetIDLIncludeFileText(Variable,OutFile)
	#We might want to add some error messages in case the OutFile is not writable

	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	return RetVal


if __name__ == '__main__':
	Variable='od550dust'
	OutFile='./AutoStart_'+Variable+'.sh'
	RetVal=WriteIDLStartScripy(OutFile)
	#WriteIDLIncludeFile(Variable, OutFile)
	#print(RetVal)

