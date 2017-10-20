"""
Module to start shell programs under the control of gnu screen
using only the python 3 language.

Exports right now the following functions:
- GetLogFileName()	     : get a unique log file name
- ExecWithLogging (*args) : execute a given command line under the control of gnu screen

################################################
Created 20170809 by Jan Griesfeller for Met Norway

Last changed: see github
################################################


"""

from .ExecWithLogging import GetLogFileName, ExecWithLogging
