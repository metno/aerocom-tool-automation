#!/usr/bin/env python3

#import sys
import pdb
import configparser
import os

def main():
	c_ConfigFile='folders.ini'
	dict_Config={}
	if os.path.isfile(c_ConfigFile):
		ReadConfig = configparser.ConfigParser()
		ReadConfig.read(c_ConfigFile)
		dict_Config['BaseDir']=[ReadConfig['folders']['BASEDIR']]
		dict_Config['FoldersToSearchIn']=ReadConfig['folders']['dir'].replace('${BASEDIR}',dict_Config['BaseDir'][0]).replace('\n','').split(',')

		for FolderToSearchIn in dict_Config['FoldersToSearchIn']:
			print(FolderToSearchIn)
			#get the directories
			if os.path.isdir(FolderToSearchIn):
				SubDirs = [FolderToSearchIn+d for d in os.listdir(FolderToSearchIn) if os.path.isdir(FolderToSearchIn+d)]
				pdb.set_trace()
				print(SubDirs)


	


if __name__ == '__main__':
    main()

