#!/bin/bash
#Simple install script

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
set -x
BinDir="${HOME}/bin"
CurrentDir=${PWD}
mkdir -p ${BinDir}
cd ${BinDir}
ln -sf ${CurrentDir}/GetModelVars/GetModelVars.py GetModelVars.py
ln -sf ${CurrentDir}/GetModelYears/GetModelYears.py GetModelYears.py
ln -sf ${CurrentDir}/GetNewFolder/GetNewFolder.py GetNewFolder.py
ln -sf ${CurrentDir}/WriteIDLIncludeFile/WriteIDLIncludeFile.py WriteIDLIncludeFile.py

IFS=$SAVEIFS

