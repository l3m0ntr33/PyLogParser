#!/usr/bin/python

import sys, re
from geoip import geolite2
import sqlite3
from dateutil.parser import parse
import datetime
import time

version="0.5"
separator = "|"
logfile=""
conffile=""
outputfile=""
dbname=""
outformat="flat"
mode="standard"
gip="no"
dateparam="no"
loopparam="no"

def usage():
	print "PyLogParser v%s - Hugo RIFFLET - @l3m0ntr33" % (version)
	print "----------------------------------------------------------"
	print "Usage: %s -i <input log file> -o <output file> -c <parsing conf file> [OPTIONS]" % (sys.argv[0])
	print "- Default output format is text file. Use -db option if you want a SQLite3 DB output."
	print "- If the output file or DB already exist, data is append to the file/DB. For DB output if schema of existing table is different you need to confirm to erase existing table."
	print ""
	print "Options:"
	print "-db <table_name> : table name for output in SQLite DB"
	print "-m : define mode"
	print "	standard (default) : only statistics, direct output to file or DB"
	print "	verbose : print results of each parsed line on screen"
	print "	test : step by step parsing for each line and regex"
	print "	silent : silent mode, no output on console."
	print "-s : define separator char for text file output, '|' by default"
	print "-geoip : add geolocation data to regex fields names starting with 'ip'"
	print "-date : try to parse the date for fields names starting with 'date' in a standard format using dateutil"
	print "-loop : watch the file every second and only add new lines. Loop mode is always silent and append data if output file or DB already exist."
	print ""

def getparam():
	i = 0
	global logfile, outputfile, conffile, mode, separator, gip, outformat, dbname, dateparam, loopparam
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
		if precparam == "-date":
			dateparam="yes"
		if precparam == "-loop":
			loopparam="yes"
		i=i+1
	#Force silent mode if loop is set
	if loopparam == "yes":
		mode = "silent"

def checkparam():
	global logfile, outputfile, conffile, mode, separator
	if ((outputfile == "") or (logfile == "") or (conffile == "")):
		usage()
		sys.exit(1)

def modeintro():
	if mode != "silent":
		print "-----------------------------------------------------------"
		print "PyLogParser v%s - Hugo RIFFLET - @l3m0ntr33" % (version)
		print "-----------------------------------------------------------"
	if mode == "standard":
		print "                  STANDARD MODE                       "
	if mode == "verbose":
		print "     VERBOSE MODE - Each result print on screen"
	if mode == "test":
		print "      TEST MODE - Line by line test for parsing"
	if mode != "silent":
		print "-----------------------------------------------------------"

def openfiles():
	if mode != "silent":
		print "Opening input file...",
	global filelog, fileoutput, fileconf
	try:
		filelog = open(logfile, "r")
		if mode != "silent":
			print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)	
	if mode != "silent":
		print "Opening output file...",
	if outformat == "flat":
		try:
			fileoutput = open(outputfile, "a")
			if mode != "silent":
				print "OK"
		except IOError, (errno, strerror):
		        print "I/O Error(%s) : %s" % (errno, strerror)
			sys.exit(1)
	if outformat == "db":
		try:
			fileoutput = sqlite3.connect(outputfile)
			if mode != "silent":
				print "OK"
		except sqlite3.error, e:
		        print "SQLite3 Error : %s" % (e)
			sys.exit(1)
	if mode != "silent":
		print "Opening config file...",
	try:
		fileconf = open(conffile, "r")
		if mode != "silent":
			print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)

def closefiles():
	if mode != "silent":
		print "Closing files...",
	global filelog, fileoutput, fileconf
	if outformat == "db":
		fileoutput.commit()
	try:
		filelog.close()
		fileoutput.close()
		fileconf.close()
		if mode != "silent":
			print "OK"
	except IOError, (errno, strerror):
	        print "I/O Error(%s) : %s" % (errno, strerror)
		sys.exit(1)

def confread():
	global conf
	global confkeys
	conf = {}
	confkeys = []
	if mode != "silent":
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
				confkeys.append(nametxt)
				if mode != "silent":
					print "Regex found - Name: " + nametxt + " - Regex: " + valuetxt,
				if (gip == "yes") and (re.search(r'^ip',nametxt) is not None):
					if mode != "silent":
						print " - IP GEOLOCATION ACTIVATED"
				else:
					if mode != "silent":
						print ""
	if mode != "silent":
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
	#27/11/2015 : add permanent insert_time field
	table_fields = "insert_time TEXT,"
	#MODIF 03/12/2015
	#for key in conf.keys():
	for index in range(len(confkeys)):
		table_fields = table_fields + confkeys[index] + " TEXT,"
		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',confkeys[index]) is not None):
			table_fields = table_fields + confkeys[index] + "_country" + " TEXT," + confkeys[index] + "_continent" + " TEXT," + confkeys[index] + "_timezone" + " TEXT," + confkeys[index] + "_lat" + " TEXT," + confkeys[index] + "_long" + " TEXT,"
	table_fields = table_fields[:-1]
	
	create_table = "CREATE TABLE " + dbname + "(" + table_fields + ");"
	drop_table = "DROP TABLE IF EXISTS " + dbname + ";"
	#Test if table already exist and schema is the same
	test_table = "select sql from sqlite_master where type = 'table' and name = '" + dbname + "';"

	try:
		dbcon.execute(test_table)
		testresult = dbcon.fetchone()
		if testresult is None:
			#Table doesn't exist
			dbcon.execute(create_table)
		else:
			#Table already exist
			if not(testresult[0].lower() == create_table[:-1].lower()):
				#Table has not the same schema
				print "-> Table " + dbname + " already exist but has not the same schema."
				print "-> Do you want to erase it ? (yes or no) ",
				keyinput = raw_input()
				if keyinput == "yes":
					dbcon.execute(drop_table)
					dbcon.execute(create_table)
				else:
					closefiles()
					sys.exit(0)	
		fileoutput.commit()
	except sqlite3.Error, e:
		print "SQLite Error : %s" % (e)
		closefiles()
		sys.exit(1)

def initfile():
	firstline = ""
	#MODIF 03/12/2015
	#for key in conf.keys():
	for index in range(len(confkeys)):
		firstline = firstline + confkeys[index] + separator

		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',confkeys[index]) is not None):
			firstline = firstline + confkeys[index] + "_country" + separator + confkeys[index] + "_continent" + separator + confkeys[index] + "_timezone" + separator + confkeys[index] + "_lat" + separator + confkeys[index] + "_long" + separator
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
	#27/11/2015 ADD PERMANENT insert_time
	data_list.append(input_dic['insert_time'])
	#MODIF 03/12/2015
	#for key in conf.keys():
	for index in range(len(confkeys)):
		data_list.append(input_dic[confkeys[index]])
		if (gip == "yes") and (re.search(r'^ip',confkeys[index]) is not None):
			data_list.append(input_dic[confkeys[index]+"_country"])
			data_list.append(input_dic[confkeys[index]+"_continent"])
			data_list.append(input_dic[confkeys[index]+"_timezone"])
			data_list.append(input_dic[confkeys[index]+"_lat"])
			data_list.append(input_dic[confkeys[index]+"_long"])
	dbcon.execute("insert into " + dbname + " values (" + ('?,' * len(data_list))[:-1] + ")", data_list)

def outfile(input_dic):
	#MODIF 03/12/2015
	#for key in conf.keys():
	for index in range(len(confkeys)):
		fileoutput.write(input_dic[confkeys[index]] + separator)
		if (gip == "yes") and (re.search(r'^ip',confkeys[index]) is not None):
			fileoutput.write(input_dic[confkeys[index]+"_country"] + separator)
			fileoutput.write(input_dic[confkeys[index]+"_continent"] + separator)
			fileoutput.write(input_dic[confkeys[index]+"_timezone"] + separator)
	fileoutput.write("\n")

def parseline(logline):
	result = {}
	if mode == "test":
		print "LOG LINE :"
		print logline
	#27/11/2015 ADD PERMANENT insert_time FIELD
	result['insert_time']=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
	#MODIF 03/12/2015
	#for key in conf.keys():
	for index in range(len(confkeys)):
		match = re.search(r"" + conf[confkeys[index]],logline)
		try:
			regres = match.group(1)
			#DATE PARSING ADDON
			if (dateparam == "yes") and (re.search(r'^date',confkeys[index]) is not None):
				result[confkeys[index]] = parse(regres, fuzzy=True).isoformat()
			else:
				result[confkeys[index]] = regres
		except:
			regres = "-"
			result[confkeys[index]] = regres
		if mode == "test":
			print "Name: " + confkeys[index] + " - Regex: " + conf[confkeys[index]] 
			print "Result: " + result[confkeys[index]]
			raw_input()

		#IP GEOLOCATION ADDON
		if (gip == "yes") and (re.search(r'^ip',confkeys[index]) is not None):
			#CONTROL INPUT FIELD IS IP ADDR
			if re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',regres) is not None:
				geoloc = geolite2.lookup(regres)
				if geoloc is not None:
					if geoloc.country is not None:
						result[confkeys[index]+"_country"] = geoloc.country
					else:
						result[confkeys[index]+"_country"] = "-"
					if geoloc.continent is not None:
						result[confkeys[index]+"_continent"] = geoloc.continent
					else:
						result[confkeys[index]+"_continent"] = "-"
					if geoloc.timezone is not None:
						result[confkeys[index]+"_timezone"] = geoloc.timezone
					else:
						result[confkeys[index]+"_timezone"] = "-"
					if geoloc.location is not None:
						result[confkeys[index]+"_lat"] = geoloc.location[0]
						result[confkeys[index]+"_long"] = geoloc.location[1]
					else:
						result[confkeys[index]+"_lat"] = "-"
						result[confkeys[index]+"_long"] = "-"
				else:
					result[confkeys[index]+"_country"] = "-"
					result[confkeys[index]+"_continent"] = "-"
					result[confkeys[index]+"_timezone"] = "-"
					result[confkeys[index]+"_lat"] = "-"
					result[confkeys[index]+"_long"] = "-"
			else:
				result[confkeys[index]+"_country"] = "-"
				result[confkeys[index]+"_continent"] = "-"
				result[confkeys[index]+"_timezone"] = "-"
				result[confkeys[index]+"_lat"] = "-"
				result[confkeys[index]+"_long"] = "-"
			if mode == "test":
				print "Name: " + confkeys[index] + "_country - Geolite2" 
				print "Result: " + str(result[confkeys[index]+"_country"])
				raw_input()
				print "Name: " + confkeys[index] + "_continent - Geolite2" 
				print "Result: " + str(result[confkeys[index]+"_continent"])
				raw_input()
				print "Name: " + confkeys[index] + "_timezone - Geolite2" 
				print "Result: " + str(result[confkeys[index]+"_timezone"])
				print "Name: " + confkeys[index] + "_lat - Geolite2" 
				print "Result: " + str(result[confkeys[index]+"_lat"])
				print "Name: " + confkeys[index] + "_long - Geolite2" 
				print "Result: " + str(result[confkeys[index]+"_long"])
				raw_input()

	if mode == "test":
		for res in result.keys():
			print str(result[res]) + separator,
		print ""
		print "------------------------------------------------------"
	if mode == "verbose":
		for res in result.keys():
			print str(result[res]) + separator,
		print ''
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

loopbit = True
#If loop mode directly go to end of file
if loopparam == "yes":
	filelog.seek(0,2)
while loopbit:
	line = filelog.readline()
	if line:
		#Test mode
		#time.sleep(1)
		#fileoutput.commit()
		#
		parseline(line)
		if mode == "standard":
			i = i+1
			prog = float(i) / float(loglinecount)
			update_progress(prog)
	else:
		if loopparam == "yes":
			if outformat == "db":
				fileoutput.commit()
			time.sleep(1)
		else:
			loopbit = False

if mode == "standard":
	print "------------------------------------------------------"

closefiles()
