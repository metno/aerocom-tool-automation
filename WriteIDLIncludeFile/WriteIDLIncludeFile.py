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

def GetIDLIncludeFileText(Variable, Filename):
	#function to store the include files
	#for now there is a dictionary entry named 'common' that at this point all cariables will get
	#and a variable specific part that uses the aerocom variable name (NOT the Aerocom-tools var 
	#name) as key

	#the htap region names are left out here because they use puxel based filters that need to be
	#in the model resolution

	dict_IncludeFileData={}
	dict_IncludeFileData['NOSUBVARS']= """
		i_ReadSubVarsFlag=0
	"""
	#for the next one nedds to define the subvars in a separate section as well
	dict_IncludeFileData['SUBVARS']= """
		i_ReadSubVarsFlag=1
	"""
	dict_IncludeFileData['od550dust']= """
		c_ModelVars=['OD550_DUST']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['COMMON']= """
		i_PlotMonthlyFlag=1
		i_VerboseFlag=1
		i_areaweightflag=1 
		c_modelmonths=['01','02','03','04','05','06','07','08','09','10','11','12']
		i_PlotZonalMeansFlag=1
		i_PlotModelAERONETTimeSeriesFlag=1
		i_PlotAERONETTimeseriesPlotArr=[iC_YM]
		s_PlotTableFlag=['SCORE','SCATTERLOG','SCATTERDENSITY','HISTO','SITELOCATION','ZONALOBS','STATMAP-BIAS','STATMAP-R']
		c_MicStationFilters=['WORLD','AUSTRALIA','NAFRICA','NAMERICA','SAMERICA','EUROPE','EASTASIA','INDIA','CHINA','WORLD-wMOUNTAINS']
		c_TimeSlots=[c_ModelMonths]
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=È || MY =3 || MYSeasons =11 
		i_MakePNG=1
		i_SendFlag=1
	"""
	dict_IncludeFileData['od550aer']= """
		c_ModelVars=['OD550_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['od550gt1aer']= """
		c_ModelVars=['OD550GT1_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['od550lt1aer']= """
		c_ModelVars=['OD550LT1_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['od550dust']= """
		c_ModelVars=['OD550_DUST']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""

	#what we return might depend on the variables and some features at some point
	#but keep it simple for now, but save space with the common block

	RetDummy=(dict_IncludeFileData[Variable]+dict_IncludeFileData['NOSUBVARS']+
		dict_IncludeFileData['COMMON'])

	OutHandle=open(Filename, 'w')
	BytesWritten=OutHandle.write(RetDummy)
	return RetDummy.strip()

		

def WriteIDLIncludeFile(Variable, OutFile, VerboseFlag=False, DebugFlag=False):
	
	RetVal=GetIDLIncludeFileText(Variable,OutFile)
	#We might want to add some error messages in case the OutFile is not writable

	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	return RetVal


if __name__ == '__main__':
	Variable='od550dust'
	OutFile='./Include.od550aer.pro'
	RetVal=WriteIDLIncludeFile(Variable, OutFile)
	#WriteIDLIncludeFile(Variable, OutFile)
	#print(RetVal)

