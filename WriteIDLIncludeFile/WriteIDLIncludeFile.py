#!/usr/bin/env python3

################################################################
# WriteIDLIncludeFile.py
#
# program to write an IDL include file for a given aerocom
# variable.
# The system used i
#
#################################################################
# Created 20170208 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

import pdb
import argparse 
import sys
import os

def GetIDLIncludeFileText(Group, Variable, all=False):
	#function to store and return parts of include files
	#The dictionary holding the include file data is divided in several sections (sub dictionaries)
	#-COMMON
	# Holds the common part of the include file. All include files will get this part
	# Note that these parameters might get overwritten later on
	#
	#-FLAGS
	# Holds single flags that can be switched on via command line options
	# e.g. NOSEND to switch off the transfer of the resulting images to the web server
	#
	#-VARS
	# Holds the variable specific part of the include file
	# Also defines variable groups
	#
	#-OBSNETWORKS
	# defines the supported obs networks
	# Note that these are only the obs networks that can be selected manually
	# If you use the standard obs networks defined by the aerocom-tools, all are supported


	#PLEASE NOTE THAT THE VARIABLE NAMES ARE ACCORDING TO THE AEROCOM PROTOCOL 
	#AND NOT ACCORDING TO THE AEROCOM-TOOLS
	
	#
	#the htap region names are left out in the common block,
	#because they use puxel based filters that need to be
	#in the model resolution
	#If we want to include that, we need an automatism to calculate the pixel based filters in model 
	#resolution

	dict_IncludeFileData={}
	#common block
	#values might get overwritten later on
	dict_IncludeFileData['COMMON']={}
	dict_IncludeFileData['COMMON']['COMMON']= """
		i_PlotMonthlyFlag=1
		i_VerboseFlag=1
		i_areaweightflag=1 
		c_modelmonths=['01','02','03','04','05','06','07','08','09','10','11','12']
		i_PlotZonalMeansFlag=1
		i_PlotModelAERONETTimeSeriesFlag=1
		i_PlotAERONETTimeseriesPlotArr=[iC_YM]
		s_PlotTableFlag=['SCORE','SCATTERLOG','SCATTERDENSITY','HISTO','SITELOCATION','ZONALOBS','STATMAP-BIAS','STATMAP-R']
		c_MicStationFilters=['WORLD','AUSTRALIA','NAFRICA','NAMERICA','SAMERICA','EUROPE','EASTASIA','ASIA','INDIA','CHINA','WORLD-wMOUNTAINS']
		c_TimeSlots=[c_ModelMonths]
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=È || MY =3 || MYSeasons =11 
		i_MakePNG=1
	"""
	############ supported special flags #############
	dict_IncludeFileData['FLAGS']={}
	dict_IncludeFileData['FLAGS']['NOSUBVARS']= """
		i_ReadSubVarsFlag=0
	"""
	#for the next one needs to define the subvars in a separate section as well
	dict_IncludeFileData['FLAGS']['SUBVARS']= """
		i_ReadSubVarsFlag=1
	"""
	dict_IncludeFileData['FLAGS']['NOSEND']="""
		i_SendFlag=0
	"""
	dict_IncludeFileData['FLAGS']['SEND']="""
		i_SendFlag=1
	"""
	dict_IncludeFileData['FLAGS']['EXPORT']="""
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
		s_PlotTableFlag=['SITELOCATION']
		i_WriteStationValues=3
	"""
	dict_IncludeFileData['FLAGS']['HTAPFILTERS']= """
		c_MicStationFilters=['RBUhtap','MCAhtap','SAMhtap','MDEhtap','SAFhtap','NAFhtap','PANhtap', 'EAShtap', 'SAShtap', $
		'EURhtap','OCNhtap','SEAhtap', 'LANDhtap','NAMhtap','ASIA','WORLD','NAFRICA','NAMERICA','SAMERICA',$
		'EUROPE','EASTASIA','INDIA','CHINA','WORLD-wMOUNTAINS']
	"""
	dict_IncludeFileData['FLAGS']['HTAPFILTERSONLY']= """
		c_MicStationFilters=['RBUhtap','MCAhtap','SAMhtap','MDEhtap','SAFhtap','NAFhtap','PANhtap', 'EAShtap', 'SAShtap', $
		'EURhtap','OCNhtap','SEAhtap', 'LANDhtap','NAMhtap']
	"""
	dict_IncludeFileData['FLAGS']['AODTRENDONLY']="""
		c_MicStationFilters=['AODTREND']
	"""
	dict_IncludeFileData['FLAGS']['AODTREND95ONLY']="""
		c_MicStationFilters=['AODTREND95']
	"""
	dict_IncludeFileData['FLAGS']['AODTRENDS']="""
		c_MicStationFilters=['AODTREND95TO12','AODTREND','AODTREND95']
	"""
	############ Variables #######################
	dict_IncludeFileData['VARS']={}
	#dict_IncludeFileData['VARS']['']="""
		#c_ModelVars=['']
	#"""
	dict_IncludeFileData['VARS']['scatc550dryaer']="""
		c_ModelVars=['SCATC550DRY_AER']
		i_ObsNetworktype=[iC_ObsNet_EBASMultiColumn]
	"""
	dict_IncludeFileData['VARS']['ec3553daer']="""
		c_ModelVars=['EC3553D_AER']
		I_PLOTPROFILESFLAG=4
		i_ReadSubVarsFlag=1
		c_SubVars=strarr(n_elements(c_modelvars),1)
		c_SubVars[*,*]=['DUMMY']
		c_SubVars[0,0:0]=['Z3D'];,'EC5503DAER_DRY']
	"""
	dict_IncludeFileData['VARS']['ec5323daer']="""
		c_ModelVars=['EC5323D_AER']
		I_PLOTPROFILESFLAG=4
		i_ReadSubVarsFlag=1
		c_SubVars=strarr(n_elements(c_modelvars),1)
		c_SubVars[*,*]=['DUMMY']
		c_SubVars[0,0:0]=['Z3D'];,'EC5503DAER_DRY']
	"""
	dict_IncludeFileData['VARS']['od550aer']= """
		c_ModelVars=['OD550_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['VARS']['od550csaer']= """
		c_ModelVars=['OD550CS_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['VARS']['od550gt1aer']= """
		c_ModelVars=['OD550GT1_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['VARS']['od550lt1aer']= """
		c_ModelVars=['OD550LT1_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['VARS']['od550dust']= """
		c_ModelVars=['OD550_DUST']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['VARS']['ang4487aer']= """
		c_ModelVars=['ANG4487_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['VARS']['ang4487csaer']= """
		c_ModelVars=['ANG4487CS_AER']
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['VARS']['wetdust']="""
		c_ModelVars=['WET_DUST']
	"""
	dict_IncludeFileData['VARS']['wetso4']="""
		c_ModelVars=['WET_SO4']
	"""
	dict_IncludeFileData['VARS']['wetbc']="""
		c_ModelVars=['WET_BC']
	"""
	dict_IncludeFileData['VARS']['wetpom']="""
		c_ModelVars=['WET_POM']
	"""
	dict_IncludeFileData['VARS']['wetss']="""
		c_ModelVars=['WET_SS']
	"""

	dict_IncludeFileData['VARS']['emidust']="""
		c_ModelVars=['EMI_DUST']
	"""
	dict_IncludeFileData['VARS']['emiso4']="""
		c_ModelVars=['EMI_SO4']
	"""
	dict_IncludeFileData['VARS']['emibc']="""
		c_ModelVars=['EMI_BC']
	"""
	dict_IncludeFileData['VARS']['emipom']="""
		c_ModelVars=['EMI_POM']
	"""
	dict_IncludeFileData['VARS']['emiss']="""
		c_ModelVars=['EMI_SS']
	"""

	dict_IncludeFileData['VARS']['drydust']="""
		c_ModelVars=['DRY_DUST']
	"""
	dict_IncludeFileData['VARS']['dryso4']="""
		c_ModelVars=['DRY_SO4']
	"""
	dict_IncludeFileData['VARS']['drybc']="""
		c_ModelVars=['DRY_BC']
	"""
	dict_IncludeFileData['VARS']['drypom']="""
		c_ModelVars=['DRY_POM']
	"""
	dict_IncludeFileData['VARS']['dryss']="""
		c_ModelVars=['DRY_SS']
	"""
	dict_IncludeFileData['VARS']['depdust']="""
		c_ModelVars=['DEP_DUST']
	"""
	dict_IncludeFileData['VARS']['depso4']="""
		c_ModelVars=['DEP_SO4']
	"""
	dict_IncludeFileData['VARS']['depbc']="""
		c_ModelVars=['DEP_BC']
	"""
	dict_IncludeFileData['VARS']['deppom']="""
		c_ModelVars=['DEP_POM']
	"""
	dict_IncludeFileData['VARS']['depss']="""
		c_ModelVars=['DEP_SS']
	"""
###
	dict_IncludeFileData['VARS']['seddust']="""
		c_ModelVars=['SED_DUST']
	"""
	dict_IncludeFileData['VARS']['sedso4']="""
		c_ModelVars=['SED_SO4']
	"""
	dict_IncludeFileData['VARS']['sedbc']="""
		c_ModelVars=['SED_BC']
	"""
	dict_IncludeFileData['VARS']['sedpom']="""
		c_ModelVars=['SED_POM']
	"""
	dict_IncludeFileData['VARS']['sedss']="""
		c_ModelVars=['SED_SS']
	"""
###
	dict_IncludeFileData['VARS']['loaddust']="""
		c_ModelVars=['LOAD_DUST']
	"""
	dict_IncludeFileData['VARS']['loadso4']="""
		c_ModelVars=['LOAD_SO4']
	"""
	dict_IncludeFileData['VARS']['loadbc']="""
		c_ModelVars=['LOAD_BC']
	"""
	dict_IncludeFileData['VARS']['loadpom']="""
		c_ModelVars=['LOAD_POM']
	"""
	dict_IncludeFileData['VARS']['loadss']="""
		c_ModelVars=['LOAD_SS']
	"""
###
###
	dict_IncludeFileData['VARS']['sconcbc']="""
		c_ModelVars=['SCONC_BC']
	"""
	dict_IncludeFileData['VARS']['sconcdust']="""
		c_ModelVars=['SCONC_DUST']
	"""
	dict_IncludeFileData['VARS']['sconcnh3']="""
		c_ModelVars=['SCONC_NH3']
	"""
	dict_IncludeFileData['VARS']['sconcnh4']="""
		c_ModelVars=['SCONC_NH4']
	"""
	dict_IncludeFileData['VARS']['sconcno2']="""
		c_ModelVars=['SCONC_NO2']
	"""
	dict_IncludeFileData['VARS']['sconcno3']="""
		c_ModelVars=['SCONC_NO3']
	"""
	dict_IncludeFileData['VARS']['sconcpm10']="""
		c_ModelVars=['SCONC_PM10']
	"""
	dict_IncludeFileData['VARS']['sconcpm25']="""
		c_ModelVars=['SCONC_PM25']
	"""
	dict_IncludeFileData['VARS']['sconcpom']="""
		c_ModelVars=['SCONC_POM']
	"""
	dict_IncludeFileData['VARS']['sconcso4']="""
		c_ModelVars=['SCONC_SO4']
	"""
	dict_IncludeFileData['VARS']['sconcso2']="""
		c_ModelVars=['SCONC_SO2']
	"""
	dict_IncludeFileData['VARS']['sconctno3']="""
		c_ModelVars=['SCONC_TNO3']
	"""
	dict_IncludeFileData['VARS']['sconcss']="""
		c_ModelVars=['SCONC_SS']
	"""
	dict_IncludeFileData['VARS']['sconcoa']="""
		c_ModelVars=['SCONC_OA']
	"""
	dict_IncludeFileData['VARS']['vmro3']="""
		c_ModelVars=['VMR_O3']
	"""
	dict_IncludeFileData['VARS']['vmrco']="""
		c_ModelVars=['VMR_CO']
	"""
	dict_IncludeFileData['VARS']['vmr3do3']="""
		c_ModelVars=['VMR3D_O3']
		i_ReadSubVarsFlag=1
		c_SubVars=strarr(n_elements(c_modelvars),7)
		c_SubVars[*,*]=['DUMMY']
		c_SubVars[0,0]=['PMID']
		c_ObsNetworkDataType=['D']
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
		I_PLOTPROFILESFLAG=4
		i_ReadStationBasedModelData=1
	"""
	#dict_IncludeFileData['VARS']['']="""
		#c_ModelVars=['']
	#"""
	########### supported variable groups ################
	dict_IncludeFileData['VARS']['ALL']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=['ALL']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
	"""
	dict_IncludeFileData['VARS']['mapsannualod']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='D' 
		c_ModelVars=[OD550_AER','OD550GT1_AER','OD550LT1_AER','ANG4487_AER','OD550_DUST','OD550_SO4','OD550_BC','OD550_POM','OD550_SS']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['mapsannual']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=['OD550_AER','OD550GT1_AER','OD550LT1_AER','ANG4487_AER','ABS550_AER','ABSC550_AER','SSA_BC','SSA_AER','ABS550_BC', $
'SCONC_DUST','SCONC_SO4','SCONC_BC','SCONC_POM','SCONC_SS', 'SCONC_NO3', 'SCONC_NH3',$
'LOAD_DUST','LOAD_SO4','LOAD_BC','LOAD_POM','LOAD_SS','LOAD_NO3', 'LOAD_NH3', $
'OD550_DUST','OD550_SO4','OD550_BC','OD550_POM','OD550_SS']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['mapsbc']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=['ABS550_AER','ABSC550_AER','SSA_BC','SSA_AER','ABS550_BC', 'ABS550_DUST',$ 
		 'SCONC_BC','EMI_BC','LOAD_BC','LOAD_DUST','EMI_DUST','SCONC_DUST',$
		 'WET_BC','DEP_BC','OD550_BC','OD550_DUST','MABS550_BC','MABS550_AER', $
		 'SWTOAAS_BCFFANT','SWTOAAS_BBANT','SWTOACS_BCFFANT','SWTOACS_BBANT']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['mapsdust']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=[c_ModelVars=['OD550_AER','OD550GT1_AER','OD550LT1_AER','ANG4487_AER','ABS550_AER', $
			'SCONC_DUST','EMI_DUST','LOAD_DUST','WET_DUST','DRY_DUST','SED_DUST','DEP_DUST','OD550_DUST']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['mapsfluxes']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=['EMI_DUST','EMI_SO4','EMI_BC','EMI_POM','EMI_SS', 'EMI_SO2','EMI_DMS',$
			'WET_DUST','WET_SO4','WET_BC','WET_POM','WET_SS', $
			'DEP_DUST','DEP_SO4','DEP_BC','DEP_POM','DEP_SS', $
			'DRY_DUST','DRY_SO4','DRY_BC','DRY_POM','DRY_SS', $
			'SED_DUST','SED_SO4','SED_BC','SED_POM','SED_SS']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['mapsod']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','EUROPE','CWE1','DWE1','DWE2']
		c_ModelVars=['OD550_AER','OD550_DUST','OD550_SO4','OD550_BC','OD550_OA','OD550_SS','OD550_NO3','OD550_SOA','OD550_NH4']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['maps']="""
		i_areaweightflag=1
		i_ObsNetworktype=[iC_ObsNet_None]
		c_ModelDataType='M' 
		c_MicStationFilters=['WORLD','NAFRICA','NAMERICA','EUROPE','EASTASIA']
		c_ModelVars=['OD550_AER','OD550GT1_AER','OD550LT1_AER','ANG4487_AER','ABS550_AER','ABSC550_AER','SSA_BC','SSA_AER','ABS550_BC', $
			'SCONC_DUST','SCONC_SO4','SCONC_BC','SCONC_POM','SCONC_SS', $
			'LOAD_DUST','LOAD_SO4','LOAD_BC','LOAD_POM','LOAD_SS', $
			'OD550_DUST','OD550_SO4','OD550_BC','OD550_POM','OD550_SS']
		i_PlotMapFlag=11 ; none=0 || M=1 || Y=2 || MY=3
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
	"""
	dict_IncludeFileData['VARS']['forcingmaps']="""
		c_ModelVars=['SWTOAAS_ANT','SWTOAAS_BCFFANT','SWTOAAS_SO4ANT','SWTOAAS_OAFFANT','SWTOAAS_SOAANT',$
		'SWTOAAS_BBANT','SWTOAAS_NO3ANT','SWTOACS_ANT','SWTOACS_BCFFANT','SWTOACS_SO4ANT',$
		'SWTOACS_OAFFANT','SWTOACS_SOAANT','SWTOACS_BBANT','SWTOACS_NO3ANT']
		c_ModelDataType='M' 
		i_ObsNetworktype=[iC_ObsNet_None]
		i_PlotZonalMeansFlag=0
		i_PlotModelAERONETTimeSeriesFlag=0
		s_PlotTableFlag=['']
	"""

	########### Supported Obs networks #####################
	dict_IncludeFileData['OBSNETWORKS']={}
	dict_IncludeFileData['OBSNETWORKS']['AERONETSun2.0']= """
		i_ObsNetworktype=[iC_ObsNet_AeronetSunRaw20]
	"""
	dict_IncludeFileData['OBSNETWORKS']['AERONETSunNRT']= """
		i_ObsNetworktype=[iC_ObsNet_AeronetSunNRT]
	"""
	dict_IncludeFileData['OBSNETWORKS']['EBASMC']= """
		i_ObsNetworktype=[iC_ObsNet_EBASMultiColumn]
	"""
	dict_IncludeFileData['OBSNETWORKS']['EAAQeRep']= """
		i_ObsNetworktype=[iC_ObsNet_AirbaseEEA]
	"""
	dict_IncludeFileData['OBSNETWORKS']['AeronetSunSDADaily']= """
		i_ObsNetworktype=[iC_ObsNet_AeronetSunSDADaily]
	"""
	dict_IncludeFileData['OBSNETWORKS']['AeronetSunV3L15Daily']= """
		i_ObsNetworktype=[iC_ObsNet_AeronetSunV3L15Daily]
	"""



	#what we return might depend on the variables and some features at some point
	#but keep it simple for now, but save space with the common block

	if all == True:
		RetDummy=dict_IncludeFileData
	else:
		RetDummy=dict_IncludeFileData[Group][Variable]

	return RetDummy

####################################################################################	

def WriteIDLIncludeFile(dict_Param, VerboseFlag=False, DebugFlag=False, ExitFlag=False):
	#In this procedure we put together the pieces the user wants to an IDL include file
	
	OutFile=dict_Param['IDLOutFile']
	RetValArr=[]
	#Handle specialities
	#This is the standard:
	RetValArr.append(GetIDLIncludeFileText('COMMON','COMMON'))
	RetValArr.append(GetIDLIncludeFileText('FLAGS','NOSUBVARS'))
	RetValArr.append(GetIDLIncludeFileText('FLAGS','SEND'))
	
	##################################################################################
	#Block for needed parts of the IDL include file
	#Or parts where the user should be notified if he/she did an error
	##################################################################################
	try:
		RetValArr.append(GetIDLIncludeFileText('VARS',dict_Param['VarName']))
	except KeyError:
		dict_SupportStruct=GetIDLIncludeFileText('nogroup','whatever', all=True)
		SupportedVars=','.join(sorted(dict_SupportStruct['VARS'].keys()))
		sys.stderr.write('ERROR: Variable name "'+dict_Param['VarName']+'" not yet supported.\n')
		sys.stderr.write('Supported variables are: '+SupportedVars+'.\n')
		sys.stderr.write('Exiting now.\n')
		sys.exit(1)

	#user specific obs network name
	#fail to make sure the user understands the obs network he/she is using
	
	if 'ObsNetworkName' in dict_Param.keys():
		try:
			RetValArr.append(GetIDLIncludeFileText('OBSNETWORKS',dict_Param['ObsNetworkName']))
		except KeyError:
			dict_SupportStruct=GetIDLIncludeFileText('nogroup','whatever', all=True)
			SupportedNets=','.join(sorted(dict_SupportStruct['OBSNETWORKS'].keys()))
			sys.stderr.write('ERROR: Obs network name "'+dict_Param['ObsNetworkName']+'" not yet supported or wrong.\n')
			sys.stderr.write('Supported Obs networks are: '+SupportedNets+'.\n')
			sys.stderr.write('Exiting now.\n')
			sys.exit(1)

	##################################################################################
	#block for the optional parts of the IDL include file
	##################################################################################
	#user supplied plot regions
	try:
		RetValArr.append("c_MicStationFilters=['"+dict_Param['PlotRegions'].replace(",","','")+"']")
	except KeyError:
		pass
	
	#no send flag
	if 'NOSEND' in dict_Param.keys():
		if dict_Param['NOSEND'] is True:
			RetValArr.append(GetIDLIncludeFileText('FLAGS','NOSEND'))
	#include HTAP filters
	if 'HTAPFILTERS' in dict_Param.keys():
		RetValArr.append(GetIDLIncludeFileText('FLAGS','HTAPFILTERS'))
			
	#include AODTRENDS filters
	if 'AODTRENDS' in dict_Param.keys():
		RetValArr.append(GetIDLIncludeFileText('FLAGS','AODTRENDS'))
			
	#include AODTRENDS filters
	if 'EXPORTOBSDATA' in dict_Param.keys():
		RetValArr.append(GetIDLIncludeFileText('FLAGS','EXPORT'))
	
	#RetValArr.append(GetIDLIncludeFileText(''))
	#RetValArr.append(GetIDLIncludeFileText(''))
	#RetValArr.append(GetIDLIncludeFileText(''))
	#RetValArr.append(GetIDLIncludeFileText(''))
	#RetValArr.append(GetIDLIncludeFileText(''))
	#RetValArr.append(GetIDLIncludeFileText(''))
	#We might want to add some error messages in case the OutFile is not writable
	RetValArr.append('')
	RetVal='\n'.join(RetValArr)
	OutHandle=open(OutFile, 'w')
	BytesWritten=OutHandle.write(RetVal)
	OutHandle.flush()
	os.fsync(OutHandle.fileno())


	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	return RetVal

####################################################################################

def WriteModellistFile(OutFile, Models, Years, ObsYears, VerboseFlag=False, DebugFlag=False):

	DataArr=[]
	DataArr.append("#file created by the aerocom automation tools")
	DataArr.append("c_Years=('"+Years.replace(',',"' '")+"')")
	if isinstance(Models,list):
		DataArr.append("c_Models=('"+"' '".join(Models)+"')")
	else:
		DataArr.append("c_Models=('"+Models+"')")
	DataArr.append("c_ObsYears=('"+ObsYears.replace(',',"' '")+"')")
	DataArr.append("")

	RetVal='\n'.join(DataArr)
	OutHandle=open(OutFile, 'w')

	BytesWritten=OutHandle.write(RetVal)
	OutHandle.flush()
	os.fsync(OutHandle.fileno())

	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	return RetVal

####################################################################################

if __name__ == '__main__':

	#Get the constant dictionary to fill the help file accordingly
	dict_SupportStruct=GetIDLIncludeFileText('nogroup','whatever', all=True)
	SupportedObsNetworks=', '.join(sorted(dict_SupportStruct['OBSNETWORKS'].keys()))

	dict_Param={}
	parser = argparse.ArgumentParser(description='Write IDL include file and model list file for the aerocom-tools \n\nexample:\nWriteIDLIncludeFile.py od550gt1aer IASI_DLR.v5.2.All,IASI_DLR.v5.2.AN,IASI_DLR.v5.2.DN ../../aerocom-tools/batching/CCI_IASI_od550gt1aer.pro ../../aerocom-tools/batching/CCI_IASI_DLR.v5.2.txt 2007,2008,2009,2010,2011,2012,2013,2014,2015\n\n')
	parser.add_argument("variable", help="variable name to use; Only one variable usable")
	parser.add_argument("model", help="model names to use; can be a comma separated list; use OBSERVATIONS-ONLY for no model")
	parser.add_argument("idloutfile", help="name of the IDL include file")
	parser.add_argument("listoutfile", help="name of the modellist file")
	parser.add_argument("years", help="years to run; can be a comma separated list")
	parser.add_argument("-o","--obsnetwork", help="observations network. Supported are "+SupportedObsNetworks+". If not used the standard obs network name from the aerocom-tools will be used")
	parser.add_argument("--plotregions", help="plot regions for map based plots to use; can be a comma separated list; e.g. WORLD,EUROPE. If not used a standard set of regions will be used")
	parser.add_argument("--obsyear", help="observation years to run; use 9999 for climatology, leave out for same as model year")
	parser.add_argument("-n","--nosend", help="switch off webserver upload", action='store_true')
	parser.add_argument("-l","--listvars", help="list the supported variables", action='store_true')
	parser.add_argument("--htapfilters", help="also include the HTAP pixel based filters",action='store_true')
	parser.add_argument("--aodtrends", help="run only the filters AODTREND and AODTREND95",action='store_true')
	parser.add_argument("--exportobsdata", help="export the obs data to text files",action='store_true')
	#parser.add_argument("--", help="")

	args = parser.parse_args()

	if args.listvars:
		SupportedVars=','.join(sorted(dict_SupportStruct['VARS'].keys()))
		sys.stderr.write('Supported variables are: '+SupportedVars+'.\n')
		sys.exit(1)

	if args.variable:
		dict_Param['VarName']=args.variable
		
	if args.model:
		dict_Param['ModelName']=args.model.split(',')

	if args.obsnetwork:
		dict_Param['ObsNetworkName']=args.obsnetwork

	if args.plotregions:
		dict_Param['PlotRegions']=args.plotregions

	if args.idloutfile:
		dict_Param['IDLOutFile']=args.idloutfile

	if args.listoutfile:
		dict_Param['ListOutFile']=args.listoutfile

	if args.years:
		dict_Param['Years']=args.years

	if args.obsyear:
		dict_Param['ObsYear']=args.obsyear
	else:
		sys.stderr.write("WARNING: No observation year provided. Falling back to using the model years\n")
		dict_Param['ObsYear']='0000'

	if args.nosend:
		dict_Param['NOSEND']=args.nosend

	if args.htapfilters:
		dict_Param['HTAPFILTERS']=args.htapfilters

	if args.aodtrends:
		dict_Param['AODTRENDS']=args.aodtrends

	if args.exportobsdata:
		dict_Param['EXPORTOBSDATA']=args.exportobsdata

	#if '' not in dict_Param.keys():
	#pdb.set_trace()
	RetVal=WriteIDLIncludeFile(dict_Param,DebugFlag=False)
	RetVal=WriteModellistFile(dict_Param['ListOutFile'], dict_Param['ModelName'], dict_Param['Years'], dict_Param['ObsYear'])

	sys.stderr.write("The files \n"+dict_Param['IDLOutFile']+"\nand\n"+dict_Param['ListOutFile']+"\n")
	sys.stderr.write("were written\n")
	#sys.stderr.write("You can now use the command ")
	#print(RetVal)

