# Author: Ankur Tyagi (Warlock_ankur)
# Framework used: Scrappy

import os
import sys

if len(sys.argv) < 5:
	print "Usage: python start_ebay.py <username> <password> <bidding_status> <N>"
else:
	siteName='ebay'
	
	username = sys.argv[1]
	password = sys.argv[2]
	bidding_status = int(sys.argv[3])
	N = sys.argv[4]

	url = ''
	if bidding_status == 1:
		url = 'http://www.ebay.com/sch/Cars-Trucks-/6001/i.html?_dcat=6001'
	elif bidding_status == 2:
		url = 'http://www.ebay.com/sch/Cars-Trucks-/6001/i.html?LH_Complete=1&rt=nc'
	elif bidding_status == 3:
		url = 'http://www.ebay.com/sch/Cars-Trucks-/6001/i.html?LH_Complete=1&LH_Sold=1&rt=nc'

	os.system('copy ' + siteName + '.py ' + siteName + '/spiders/' + siteName + '.py')
	os.system('del ' + siteName + '_output.csv')
	cmd = 'scrapy crawl ' + siteName + ' -o ' + siteName + '_output.csv -t csv -a username=' + username + ' -a password=' + password + ' -a N=' + str(N) + ' -a bidding_status=' + str(bidding_status) + ' -a url="' + url + '"'
	print cmd
	os.system(cmd)
	os.system('copy ' + siteName + '_output.csv ' + siteName + '_output_`date +%Y-%m-%d`.csv')

	print 'Parsing Done!!!'
	