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
ln -sf ${CurrentDir}/GetModelDir/GetModelDir.py GetModelDir.py
ln -sf ${CurrentDir}/ModAerocomMain/ModAerocomMain.py ModAerocomMain.py
ln -sf ${CurrentDir}/folders.ini folders.ini
ln -sf ${CurrentDir}/aerocom-tool-automation.py aerocom-tool-automation.py
ln -sf ${CurrentDir}/ATAStats/ATAStats.py ATAStats.py

IFS=$SAVEIFS

