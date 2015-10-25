#!/usr/bin/python

import sys, re
from geoip import geolite2

version="0.1"
separator = "|"
logfile=""
conffile=""
outputfile=""
mode="standard"
gip="no"

def usage():
	print "PyLogParser v%s - Hugo RIFFLET - @l3m0ntr33" % (version)
	print "----------------------------------------------------------"
	print "Usage: %s -i <input log file> -o <output log file> -c <parsing conf file> [OPTIONS]" % (sys.argv[0])
	print "Options:"
	print "-m : define mode"
	print "	standard (default) : only statistics, direct output to file"
	print "	verbose : print results on screen"
	print "	test : step by step parsing"
	print "-s : define separator char, '|' by default"
	print "-geoip : add geolocation data to regex field name starting with 'ip'"
	print ""

def getparam():
	i = 0
	global logfile, outputfile, conffile, mode, separator, gip
	for param in sys.argv:
		precparam = sys.argv[i-1]
		if precparam == "-i":
			logfile = param
		if precparam == "-o":
			outputfile = param
		if precparam == "-c":
			conffile = param
		if precparam == "-m":
			mode = param
		if precparam == "-s":
			separator = param
		if precparam == "-geoip":
			gip="yes"
		i=i+1

def checkparam():
	global logfile, outputfile, conffile, mode, separator
	if ((outputfile == "") or (logfile == "") or (conffile == "")):
		usage()
		sys.exit(1)

def modeintro():
	print "-----------------------------------------------------------"
	print "PyLogParser v%s - Hugo RIFFLET - @l3m0ntr33" % (version)
	print "-----------------------------------------------------------"
	if mode == "standard":
		print "                  STANDARD MODE                       "
	if mode == "verbose":
		print "     VERBOSE MODE - Each result print on screen"
	if mode == "test":
		print "      TEST MODE - Line by line test for parsing"
	print "-----------------------------------------------------------"

def openfiles():
	print "Opening input file...",
	global filelog, fileoutput, fileconf
	try:
		filelog = open(logfile, "r")
		print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)	
	print "Opening output file...",
	try:
		fileoutput = open(outputfile, "w")
		print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)
	print "Opening config file...",
	try:
		fileconf = open(conffile, "r")
		print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)

def closefiles():
	print "Closing files...",
	global filelog, fileoutput, fileconf
	try:
		filelog.close()
		fileoutput.close()
		fileconf.close()
		print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)

def confread():
	global conf
	conf = {}
	print "------------------------------------------------------"
	print "                 READING CONFIG FILE"
	print "------------------------------------------------------"
	for line in fileconf.readlines():
		if re.search(r'^#',line) is None :
			name = re.search(r'([^;]*);',line)
			value = re.search(r';([^;]*);',line)
			if name is not None and value is not None:
				nametxt = "" + name.group(1)
				valuetxt = "" + value.group(1)
				conf[nametxt] = valuetxt
				print "Regex found - Name: " + nametxt + " - Regex: " + valuetxt,
				if (gip == "yes") and (re.search(r'^ip',nametxt) is not None):
					print " - IP GEOLOCATION ACTIVATED"
				else:
					print ""
	print "------------------------------------------------------"

def initfile():
	firstline = ""
	for key in conf.keys():
		firstline = firstline + key + separator

		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			firstline = firstline + key + "-country" + separator + key + "-continent" + separator + key + "-timezone" + separator
	fileoutput.write(firstline + "\n")
	if mode == "verbose":
		print firstline
		raw_input()

def outfile(outline):
	fileoutput.write(outline + "\n")

def parse(logline):
	result = ""
	if mode == "test":
		print "LOG LINE :"
		print logline
	for key in conf.keys():
		match = re.search(r"" + conf[key],logline)
		try:
			regres = match.group(1)
			result = result + regres + separator
		except:
			regres = "-"
			result = result + regres + separator
		if mode == "test":
			print "Name: " + key + " - Regex: " + conf[key] 
			print "Result: " + regres
			raw_input()
		
		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			#CONTROL INPUT FIELD IS IP ADDR
			if re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',regres) is not None:
				geoloc = geolite2.lookup(regres)
				if geoloc is not None:
					if geoloc.country is not None:
						result = result + geoloc.country + separator
					else:
						result + "-" + separator
					if geoloc.continent is not None:
						result = result + geoloc.continent + separator
					else:
						result + "-" + separator
					if geoloc.timezone is not None:
						result = result + geoloc.timezone + separator
					else:
						result + "-" + separator
				else:
					result = result + "-" + separator + "-" + separator + "-" + separator
			else:
				result = result + "-" + separator + "-" + separator + "-" + separator

	if mode == "test":
		print "------------------------------------------------------"
	if mode == "verbose":
		print result
	outfile(result)

def filelog_len():
	global loglinecount
	global filelog
	loglinecount = 0
	for line in filelog:
		loglinecount+=1
	filelog.seek(0,0)

## update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "="*block + " "*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

####### START #########

if len(sys.argv) < 7:
	usage()
	sys.exit(0)
else:
	getparam()

checkparam()

modeintro()

openfiles()

confread()

initfile()

filelog_len()


if mode == "standard":
	print "                  BEGIN PROCESSING"
	print "------------------------------------------------------"
	print "Total line to parse : %s" % (loglinecount)
	i = 0
	prog = 0.0
	update_progress(prog)

for line in filelog.readlines():
	parse(line)
	if mode == "standard":
		i = i+1
		prog = float(i) / float(loglinecount)
		update_progress(prog)
if mode == "standard":
	print "------------------------------------------------------"

closefiles()
