################################################################
# Taskinfo.py
#
# imitate ps -ef | grep <progname> using the psutil package
# 
# This program is part of the aerocom-tool-automation software
#
#################################################################
# Created 20170824 by Jan Griesfeller for Met Norway
#
# Last changed: See git log
#################################################################

def Taskinfo(Name, user=False, PrintInfo=False, RetNumber=False, VerboseFlag=False, DebugFlag=False):
	"""imitate ps -ef | grep <progname> using the psutil package
	"""
	import psutil, re

	RetVal=[]

	Regexp = re.compile(Name, re.IGNORECASE)
	if user is not False:
		UserRegexp = re.compile(user)
	for proc in psutil.process_iter():
		try:
			pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline','username'])
		except psutil.NoSuchProcess:
			pass
		else:
			if Regexp.match(pinfo['name']):
				if user is not False:
					if UserRegexp.match(pinfo['username']):
						RetVal.append(pinfo)
				else:
					RetVal.append(pinfo)


	if PrintInfo:
		print(RetVal)

	if VerboseFlag:
		print(RetVal)
	if DebugFlag:
		pdb.set_trace()

	if RetNumber:
		return len(RetVal)

	return RetVal
