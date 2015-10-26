#!/usr/bin/python

import sys, re
from geoip import geolite2
import sqlite3

version="0.2"
separator = "|"
logfile=""
conffile=""
outputfile=""
dbname=""
outformat="flat"
mode="standard"
gip="no"

def usage():
	print "PyLogParser v%s - Hugo RIFFLET - @l3m0ntr33" % (version)
	print "----------------------------------------------------------"
	print "Usage: %s -i <input log file> -o <output log file> -c <parsing conf file> [OPTIONS]" % (sys.argv[0])
	print "Options:"
	print "-db <table_name> : table name for output in SQLite DB"
	print "-append : append to existing output file, db or flat log file (NOT IMPLEMENTED YET)"
	print "-m : define mode"
	print "	standard (default) : only statistics, direct output to file"
	print "	verbose : print results on screen"
	print "	test : step by step parsing"
	print "-s : define separator char, '|' by default"
	print "-geoip : add geolocation data to regex field name starting with 'ip'"
	print ""

def getparam():
	i = 0
	global logfile, outputfile, conffile, mode, separator, gip, outformat, dbname
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
		if precparam == "-db":
			outformat = "db"
			dbname = param
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
	if outformat == "flat":
		try:
			fileoutput = open(outputfile, "w")
			print "OK"
		except IOError, (errno, strerror):
		        print "I/O Error(%s) : %s" % (errno, strerror)
			sys.exit(1)
	if outformat == "db":
		try:
			fileoutput = sqlite3.connect(outputfile)
			print "OK"
		except sqlite3.error, e:
		        print "SQLite3 Error : %s" % (e)
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
	if outformat == "db":
		fileoutput.commit()
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

def init():
	if outformat == "flat":
		initfile()
	if outformat == "db":
		initdb()
def initdb():
	global dbcon
	try:
		dbcon = fileoutput.cursor()
	except sqlite3.error, e:
		print "SQLite Error : %s" % (e)
		sys.exit(1)
	table_fields = ""
	for key in conf.keys():
		table_fields = table_fields + key + " TEXT,"
		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			table_fields = table_fields + key + "_country" + " TEXT," + key + "_continent" + " TEXT," + key + "_timezone" + " TEXT,"
	table_fields = table_fields[:-1]
	
	create_table = "CREATE TABLE " + dbname + "(" + table_fields + ");"
	drop_table = "DROP TABLE IF EXISTS " + dbname + ";"
	try:
		dbcon.execute(drop_table)
		dbcon.execute(create_table)
		fileoutput.commit()
	except sqlite3.Error, e:
		print "SQLite Error : %s" % (e)
		sys.exit(1)


def initfile():
	firstline = ""
	for key in conf.keys():
		firstline = firstline + key + separator

		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			firstline = firstline + key + "_country" + separator + key + "_continent" + separator + key + "_timezone" + separator
	fileoutput.write(firstline + "\n")
	if mode == "verbose":
		print firstline
		raw_input()

def output(input_dic):
	if outformat == "flat":
		outfile(input_dic)
	if outformat == "db":
		outdb(input_dic)

def outdb(input_dic):
	data_list = []
	for key in conf.keys():
		data_list.append(input_dic[key])
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			data_list.append(input_dic[key+"_country"])
			data_list.append(input_dic[key+"_continent"])
			data_list.append(input_dic[key+"_timezone"])
	dbcon.execute("insert into " + dbname + " values (" + ('?,' * len(data_list))[:-1] + ")", data_list)

def outfile(input_dic):
	for key in conf.keys():
		fileoutput.write(input_dic[key] + separator)
		if (gip == "yes") and (re.search(r'^ip',key) is not None):
			fileoutput.write(input_dic[key+"_country"] + separator)
			fileoutput.write(input_dic[key+"_continent"] + separator)
			fileoutput.write(input_dic[key+"_timezone"] + separator)
	fileoutput.write("\n")

def parse(logline):
	result = {}
	if mode == "test":
		print "LOG LINE :"
		print logline
	for key in conf.keys():
		match = re.search(r"" + conf[key],logline)
		try:
			regres = match.group(1)
			result[key] = regres
		except:
			regres = "-"
			result[key] = regres
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
						result[key+"_country"] = geoloc.country
					else:
						result[key+"_country"] = "-"
					if geoloc.continent is not None:
						result[key+"_continent"] = geoloc.continent
					else:
						result[key+"_continent"] = "-"
					if geoloc.timezone is not None:
						result[key+"_timezone"] = geoloc.timezone
					else:
						result[key+"_timezone"] = "-"
				else:
					result[key+"_country"] = "-"
					result[key+"_continent"] = "-"
					result[key+"_timezone"] = "-"
			else:
				result[key+"_country"] = "-"
				result[key+"_continent"] = "-"
				result[key+"_timezone"] = "-"
			if mode == "test":
				print "Name: " + key + "_country - Geolite2" 
				print "Result: " + result[key+"_country"]
				raw_input()
				print "Name: " + key + "_continent - Geolite2" 
				print "Result: " + result[key+"_continent"]
				raw_input()
				print "Name: " + key + "_timezone - Geolite2" 
				print "Result: " + result[key+"_timezone"]
				raw_input()

	if mode == "test":
		for res in result.keys():
			print result[res] + separator,
		print ""
		print "------------------------------------------------------"
	if mode == "verbose":
		for res in result.keys():
			print result[res] + separator,
	output(result)

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

init()

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
