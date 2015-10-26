# PyLogParser  

## NEW FEATURES WITH 0.2  
You can now choose between flat file output and SQLite3 DB file output. You just need to use the ```-db <db_name>``` specify the name of your log table inside the DB. If the table already exist it's delete.  

NEXT IMPROVEMENT : ability to append to an existing flat file or DB.

## Description    
This short script has been designed to help when you need to realize fast investigation from raw logs without having some ELK or SIEM tool for example. Usually I use combination of grep, awk and sed CLI tools to extract useful information with always the same input or output.  
I use this script to extract all useful information from logs in one command line to a CSV like format file. It is based on a configuration file where you can store all your regular expressions and re-use them when you need just by uncomment the lines you need.  
  
The script just take you're input log file and parse each line with selected regular expression and store the result in your output file with the selected seperation character.  
I also add an optionnal geo-ip module based on geolite2 Python module wich add geolocation data to each column/regex's name that begin with "ip".

## Usage  
```
Usage: PyLogParser.py -i <input log file> -o <output log file> -c <parsing conf file> [OPTIONS]
Options:
-db <table_name> : table name for output in SQLite3 DB
-append : append to existing output file, db or flat log file (NOT IMPLEMENTED YET)
-m : define mode
	standard (default) : only statistics, direct output to file
	verbose : print results on screen
	test : step by step parsing
-s : define separator char, '|' by default
-geoip : add geolocation data to regex field name starting with 'ip'
```

Mode explanation :  
* standard (default) : only print on screen information about current job and progress status bar  
* verbose : print directly on screen all the output lines  
* test : useful to test new regular expression. It's a step by step mode, where you can see result of each regex line by line from your input file.  

## Configuration file  
Very simple :  
* each line starting with # is a comment line  
* others line format ```<data_name>;<regex>;```  
  
Script use each non commented line as a data field to extract from log based on the corresponding regex. If no data match the field output is '-'.  

See the example parsing configuration file with Apache combined log format data field extractors.  

You can store in this file all your standard log format parser and use them just by uncommenting the lines you need.  

## Install dependencies  
Using pip is the easiest way :  
```
pip install pygeoip  
pip install python-geoip-geolite2  
```

## Examples  
Standard (default) mode  
```
l3m0ntr33@nob:~/PyLogParser# ./PyLogParser.py -i access_log -o result_log -c parser.conf
-----------------------------------------------------------
PyLogParser v0.1 - Hugo RIFFLET - @l3m0ntr33
-----------------------------------------------------------
                  STANDARD MODE                       
-----------------------------------------------------------
Opening input file... OK
Opening output file... OK
Opening config file... OK
------------------------------------------------------
                 READING CONFIG FILE
------------------------------------------------------
Regex found - Name: ip_host - Regex: ^([^\s]*)\s 
Regex found - Name: remote_logname - Regex: ^[^\s]*\s([^\s]*)\s 
Regex found - Name: remote_user - Regex: ^[^\s]*\s[^\s]*\s([^\s]*)\s 
Regex found - Name: time - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[([^\]]*)\] 
Regex found - Name: request - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\"]*)\" 
Regex found - Name: method - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\s]*)\s 
Regex found - Name: status - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s(\d*)\s 
Regex found - Name: byte_sent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s(\d*)\s 
Regex found - Name: referer - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"([^\"]*)\" 
Regex found - Name: user_agent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"[^\"]*\"\s\"([^\"]*)\" 
------------------------------------------------------
                  BEGIN PROCESSING
------------------------------------------------------
Total line to parse : 7207
Percent: [====================] 100% Done...
------------------------------------------------------
Closing files... OK
l3m0ntr33@nob:~/PyLogParser# 
```
  
Standard mode with IP Geoloc addon  
```
l3m0ntr33@nob:~/PyLogParser# ./PyLogParser.py -i access_log -o result_log -c parser.conf -geoip
-----------------------------------------------------------
PyLogParser v0.1 - Hugo RIFFLET - @l3m0ntr33
-----------------------------------------------------------
                  STANDARD MODE                       
-----------------------------------------------------------
Opening input file... OK
Opening output file... OK
Opening config file... OK
------------------------------------------------------
                 READING CONFIG FILE
------------------------------------------------------
Regex found - Name: ip_host - Regex: ^([^\s]*)\s  - IP GEOLOCATION ACTIVATED
Regex found - Name: remote_logname - Regex: ^[^\s]*\s([^\s]*)\s 
Regex found - Name: remote_user - Regex: ^[^\s]*\s[^\s]*\s([^\s]*)\s 
Regex found - Name: time - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[([^\]]*)\] 
Regex found - Name: request - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\"]*)\" 
Regex found - Name: method - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\s]*)\s 
Regex found - Name: status - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s(\d*)\s 
Regex found - Name: byte_sent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s(\d*)\s 
Regex found - Name: referer - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"([^\"]*)\" 
Regex found - Name: user_agent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"[^\"]*\"\s\"([^\"]*)\" 
------------------------------------------------------
                  BEGIN PROCESSING
------------------------------------------------------
Total line to parse : 7207
Percent: [====================] 100% Done...
------------------------------------------------------
Closing files... OK
l3m0ntr33@nob:~/PyLogParser# 
```
  
Test mode  
```
l3m0ntr33@nob:~/PyLogParser# ./PyLogParser.py -i access_log -o result_log -c parser.conf -m test
-----------------------------------------------------------
PyLogParser v0.1 - Hugo RIFFLET - @l3m0ntr33
-----------------------------------------------------------
      TEST MODE - Line by line test for parsing
-----------------------------------------------------------
Opening input file... OK
Opening output file... OK
Opening config file... OK
------------------------------------------------------
                 READING CONFIG FILE
------------------------------------------------------
Regex found - Name: ip_host - Regex: ^([^\s]*)\s 
Regex found - Name: remote_logname - Regex: ^[^\s]*\s([^\s]*)\s 
Regex found - Name: remote_user - Regex: ^[^\s]*\s[^\s]*\s([^\s]*)\s 
Regex found - Name: time - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[([^\]]*)\] 
Regex found - Name: request - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\"]*)\" 
Regex found - Name: method - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\s]*)\s 
Regex found - Name: status - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s(\d*)\s 
Regex found - Name: byte_sent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s(\d*)\s 
Regex found - Name: referer - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"([^\"]*)\" 
Regex found - Name: user_agent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"[^\"]*\"\s\"([^\"]*)\" 
------------------------------------------------------
LOG LINE :
50.63.194.24 - - [17/Sep/2015:06:25:30 +0200] "POST /images/lofthumbs/600x150/images/inc.php HTTP/1.0" 200 268 "-" "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"

Name: status - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s(\d*)\s
Result: 200

Name: remote_user - Regex: ^[^\s]*\s[^\s]*\s([^\s]*)\s
Result: -

Name: byte_sent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s(\d*)\s
Result: 268

Name: request - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\"]*)\"
Result: POST /images/lofthumbs/600x150/images/inc.php HTTP/1.0

Name: remote_logname - Regex: ^[^\s]*\s([^\s]*)\s
Result: -

Name: referer - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"([^\"]*)\"
Result: -

Name: user_agent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"[^\"]*\"\s\"([^\"]*)\"
Result: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0

Name: time - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[([^\]]*)\]
Result: 17/Sep/2015:06:25:30 +0200

Name: ip_host - Regex: ^([^\s]*)\s
Result: 50.63.194.24

Name: method - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\s]*)\s
Result: POST

------------------------------------------------------
LOG LINE :
50.62.177.131 - - [17/Sep/2015:06:27:52 +0200] "POST /images/lofthumbs/600x150/images/inc.php HTTP/1.0" 200 268 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48 Safari/537.36"

[...]
```
  
Verbose mode  
```
l3m0ntr33@nob:~/PyLogParser# ./PyLogParser.py -i access_log -o result_log -c parser.conf -geoip -m verbose
-----------------------------------------------------------
PyLogParser v0.1 - Hugo RIFFLET - @l3m0ntr33
-----------------------------------------------------------
     VERBOSE MODE - Each result print on screen
-----------------------------------------------------------
Opening input file... OK
Opening output file... OK
Opening config file... OK
------------------------------------------------------
                 READING CONFIG FILE
------------------------------------------------------
Regex found - Name: ip_host - Regex: ^([^\s]*)\s  - IP GEOLOCATION ACTIVATED
Regex found - Name: remote_logname - Regex: ^[^\s]*\s([^\s]*)\s 
Regex found - Name: remote_user - Regex: ^[^\s]*\s[^\s]*\s([^\s]*)\s 
Regex found - Name: time - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[([^\]]*)\] 
Regex found - Name: request - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\"]*)\" 
Regex found - Name: method - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"([^\s]*)\s 
Regex found - Name: status - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s(\d*)\s 
Regex found - Name: byte_sent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s(\d*)\s 
Regex found - Name: referer - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"([^\"]*)\" 
Regex found - Name: user_agent - Regex: ^[^\s]*\s[^\s]*\s[^\s]*\s\[[^\]]*\]\s\"[^\"]*\"\s\d*\s\d*\s\"[^\"]*\"\s\"([^\"]*)\" 
------------------------------------------------------
status|remote_user|byte_sent|request|remote_logname|referer|user_agent|time|ip_host|ip_host-country|ip_host-continent|ip_host-timezone|method|

200|-|268|POST /images/lofthumbs/600x150/images/inc.php HTTP/1.0|-|-|Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0|17/Sep/2015:06:25:30 +0200|50.63.194.24|US|NA|America/Phoenix|POST|
200|-|268|POST /images/lofthumbs/600x150/images/inc.php HTTP/1.0|-|-|Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48 Safari/537.36|17/Sep/2015:06:27:52 +0200|50.62.177.131|US|NA|America/Phoenix|POST|
200|-|11963|GET / HTTP/1.1|-|-|Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)|17/Sep/2015:06:29:55 +0200|66.249.64.86|US|NA|America/Los_Angeles|GET|

[...]
```
  