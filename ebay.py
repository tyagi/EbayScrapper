# Author: Ankur Tyagi (Warlock_ankur)
# Framework used: Scrappy

import os
import re
import re
import sys
import csv
import time
import math
import signal
import urllib2
import datetime
import traceback
import HTMLParser
from scrapy.spider import BaseSpider
from scrapy.item import Item, Field
from scrapy.selector import HtmlXPathSelector
from django.utils.encoding import smart_str, smart_unicode
from scrapy.http import FormRequest,Request,Response,HtmlResponse,XmlResponse

print 'Inside ebay!!!'
class ebayItem(Item):
	Timestamp = Field()
	Source_URL = Field()
	Source = Field()
	Posting_Datetime = Field()
	Make = Field()
	Model = Field()
	Year = Field()
	Mileage = Field()
	Transmission = Field()
	Title = Field()
	Condition = Field()
	Price = Field()
	Location = Field()
	Email = Field()
	Phone = Field()
	Preferred = Field()
	VIN = Field()
	Title_of_Ad = Field()
	Comments2 = Field()
	Asking_price = Field()
	Sale_Type = Field()
	Ended = Field()
	Report_Run_Date = Field()
	Comments = Field()
	eBay_Item_Number = Field()
	Bidding_Status = Field()
	

class ebaySpider(BaseSpider):
	name='ebay'
	log=[]
	#download_delay = 0.5
	#CONCURRENT_REQUESTS = 1

	#Get the homepage
	start_urls = ['https://signin.ebay.com/ws/eBayISAPI.dll?SignIn']
	projectName='ebay'	
	

	def __init__(self, *args, **kwargs):

		self.baseURL='http://www.ebay.com'	
		
		#Setup the parser
		self.parser = HTMLParser.HTMLParser()
		
		self.username = kwargs.get('username')
		self.password = kwargs.get('password')
		self.url = kwargs.get('url')
		self.bidding_status = int(kwargs.get('bidding_status'))
		self.N = int(kwargs.get('N'))


	def parse(self,response):
		return [FormRequest.from_response(response, formdata={'userid': self.username, 'pass': self.password}, callback=self.after_login)]


	def error(self, response):
		print 'Error on url: ', response.url

		
	def after_login(self,response):
		print '\tAfter Login:'
		print '\t'+response.url
		req = Request(url = self.url + '&_ipg=200', callback=self.parseResultPage)
		req.meta['FirstPage'] = 1
		return req
		
		
	def parseResultPage(self,response):
		print '\t'+response.url
		
		res_text = response.body.replace('\n', ' ').replace('\t', ' ').replace('\r', '')

		hxs = HtmlXPathSelector(response)

		reqs = []
		
		if response.meta['FirstPage'] == 1:
			num_results = 0
			tmp = hxs.select('//span[@class="rcnt"]/text()').extract()
			if len(tmp) > 0:
				num_results = int(tmp[0].replace(',', ''))
			if num_results > self.N:
				num_results = self.N
				
			num_pages = int(math.ceil(num_results/200.0))
			print num_pages, num_results
			
			for i in range(2, num_pages+1):
				url = self.url + '&_ipg=200&_pgn='+str(i)+'&_skc='+str(200*(i-1))
				req = Request(url, callback=self.parseResultPage)
				req.meta['FirstPage'] = 0
				reqs.append(req)
				#break
		
		links = hxs.select('//div[@id="ResultSetItems"]//table//h3/a/@href').extract()
		if len(links) == 0:
			print 'no results'

		#print links
		print '#Results: ' + str(len(links))
		i = 1
		for link in links:
			req = Request(link, callback = self.parseDetails)
			req.meta['rank'] = i
			reqs.append(req)
			i += 1
			#break
		return reqs

		
	def parseDetails(self, response):
		#f = open('dump.html', 'w')
		#f.write(response.body)
		#f.close()
	
		rank = response.meta['rank']

		res_text = response.body_as_unicode().encode('ascii', 'ignore')
		res_text = smart_str(self.parser.unescape(self.parser.unescape(res_text))).replace('\xc2\xa0','')
		res_text = res_text.replace('\n', ' ').replace('\t', ' ').replace('\r', '')
		res_text = re.subn('<script.*?</script>', '', res_text)[0]
		res_text = re.subn('<style.*?</style>', '', res_text)[0]
		hxs = HtmlXPathSelector(text=res_text)

		Item = ebayItem()
		Item['Timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		Item['Source'] = 'ebay'
		Item['Source_URL'] = response.url
		Item['Posting_Datetime'] = 'NA'
		Item['eBay_Item_Number'] = 'NA'
		Item['Make'] = 'NA'
		Item['Model'] = 'NA'
		Item['Year'] = 'NA'
		Item['Mileage'] = 'NA'
		Item['Transmission'] = 'NA'
		Item['Title'] = 'NA'
		Item['Condition'] = 'NA'
		Item['Price'] = 'NA'
		Item['Location'] = 'NA'
		Item['Email'] = 'NA'
		Item['Phone'] = 'NA'
		Item['Preferred'] = 'NA'
		Item['VIN'] = 'NA'
		Item['Title_of_Ad'] = 'NA'
		Item['Comments'] = 'NA'
		Item['Comments2'] = 'NA'
		Item['Asking_price'] = 'NA'
		Item['Sale_Type'] = 'NA'
		Item['Ended'] = 'NA'
		Item['Report_Run_Date'] = 'NA'
		
		if self.bidding_status == 1:
			Item['Bidding_Status'] = 'Active'
		elif self.bidding_status == 2:
			Item['Bidding_Status'] = 'Completed'
		elif self.bidding_status == 3:
			Item['Bidding_Status'] = 'Sold'
		else:
			Item['Bidding_Status'] = 'NA'
		
		try:
			tmp = hxs.select('//span[@id="bb_tlft"]//text()').extract()
			if len(tmp) <= 4:
				Item['Ended'] = ' '.join(tmp).strip()
			else:
				Item['Ended'] = ' '.join(hxs.select('//span[@class="vi-tm-left"]//text()').extract()).strip()
		except:
			pass
			
		try:
			Item['Report_Run_Date'] = re.findall('Report Run Date:.*?<span>(.*?)<', res_text)[0].strip()
		except:
			pass
			
		try:
			Item['Title_of_Ad'] = ''.join(hxs.select('//h1[@id="itemTitle"]/text()').extract()).strip()
		except:
			pass
			
		try:
			Item['eBay_Item_Number'] = hxs.select('//div[contains(@class,"iti-act-num")]/text()').extract()[0].strip()
		except:
			pass
			
		tables = hxs.select('//div[@class="itemAttr"]//table')
		trs = tables[-1].select('.//tr')
		attr = ''
		i = 0
		for tr in trs:
			tds = tr.select('.//td')
			for td in tds:
				i += 1
				text = ''.join(td.select('.//text()').extract()).strip()
				if (i % 2 == 1):
					attr = text
				else:
					val = text
					if (attr == 'Make:'):
						Item['Make'] = val
					elif (attr == 'Model:'):
						Item['Model'] = val
					elif (attr == 'Year:'):
						Item['Year'] = val
					elif (attr == 'Vehicle Title:'):
						Item['Title'] = val
					elif (attr == 'Mileage:'):
						Item['Mileage'] = val
					elif (attr == 'Transmission:'):
						Item['Transmission'] = val
					elif (attr == 'VIN (Vehicle Identification Number):'):
						Item['VIN'] = val

		try:
			Item['Condition'] = ''.join(hxs.select('//div[@id="vi-itm-cond"]/text()').extract()).strip()
			if Item['Condition'] == '':
				Item['Condition'] == 'NA'
		except:
			pass
			
		try:
			tmp = hxs.select('//div[@itemprop="price"]//text()').extract()
			if len(tmp) == 0:
				tmp = hxs.select('//div[contains(@class,"vi-price")]/span[1]//text()').extract()
			if len(tmp) == 0:
				tmp = hxs.select('//div[contains(@class,"vi-price-np")]/span[1]//text()').extract()
			Item['Price'] = ''.join(tmp).strip()
			Item['Asking_price'] = Item['Price']
		except:
			pass
			
		try:
			tmp = hxs.select('//div[@class="sh-loc"]/text()').extract()
			if len(tmp) == 0:
				tmp = hxs.select('//div[@class="u-flL"]/text()').extract()
			Item['Location'] = ''.join(tmp).strip()
		except:
			pass
			
		try:
			Item['Posting_Datetime'] = ''.join(hxs.select('//div[@class="vi-desc-revHistory"]/div/text()').extract()).strip()
			if Item['Posting_Datetime'] == '':
				Item['Posting_Datetime'] = 'NA'
		except:
			pass
			
		try:
			Item['Comments'] = self.removeTags(''.join(hxs.select('//div[@id="desc_div"]//text()').extract()).strip())
		except:
			pass
			
		try:
			Item['Comments2'] = ''.join(hxs.select('//td[@class="sellerNotesContent"]//text()').extract()).strip()
			if Item['Comments2'] == '':
				Item['Comments2'] == 'NA'
		except:
			pass

		try:
			tmp = hxs.select('//form[@name="viactiondetails"]//a[@role="button"]//text()').extract()
			tmp2 = []
			for val in tmp:
				val = val.strip()
				tmp2.append(val)
			if tmp2 == []:
				tmp2 = ['Buy It Now']
			Item['Sale_Type'] = ' & '.join(tmp2)
		except:
			pass

		"""try:
			comments_url = hxs.select('//iframe[@id="desc_ifr"]/@src').extract()[0].strip()
			if comments_url != '':
				req = Request(comments_url, dont_filter=True, callback=self.getComments)
				req.meta['item'] = Item
				return req
		except:
			pass
		
		try:
			offers_url = 'http://offer.ebay.com/ws/eBayISAPI.dll?ViewBids&item=' + Item['eBay_Item_Number']
			if Item['eBay_Item_Number'] != 'NA' and Item['eBay_Item_Number'] != '':
				req = Request(offers_url, dont_filter=True, callback=self.getPostingDate)
				req.meta['item'] = Item
				return req
		except:
			pass
		"""

		return Item

		
	def getComments(self, response):
		Item = response.meta['item']

		res_text = response.body_as_unicode().encode('ascii', 'ignore')
		res_text = smart_str(self.parser.unescape(self.parser.unescape(res_text))).replace('\xc2\xa0','')
		res_text = res_text.replace('\n', ' ').replace('\t', ' ').replace('\r', '')
		res_text = re.subn('<script.*?</script>', '', res_text)[0]
		res_text = re.subn('<style.*?</style>', '', res_text)[0]
		hxs = HtmlXPathSelector(text=res_text)
		
		tmp = hxs.select('//div[@id="ds_div"]//text()').extract()
		comments = ''
		for val in tmp:
			val = val.strip()
			if val != '':
				comments += val + ' '
		Item['Comments'] = comments

		try:
			offers_url = 'http://offer.ebay.com/ws/eBayISAPI.dll?ViewBids&item=' + Item['eBay_Item_Number']
			if Item['eBay_Item_Number'] != 'NA' and Item['eBay_Item_Number'] != '':
				req = Request(offers_url, dont_filter=True, callback=self.getPostingDate)
				req.meta['item'] = Item
				return req
		except:
			pass

		return Item
		
	
	def getPostingDate(self, response):
		Item = response.meta['item']

		res_text = response.body_as_unicode().encode('ascii', 'ignore')
		res_text = smart_str(self.parser.unescape(self.parser.unescape(res_text))).replace('\xc2\xa0','')
		res_text = res_text.replace('\n', ' ').replace('\t', ' ').replace('\r', '')
		res_text = re.subn('<script.*?</script>', '', res_text)[0]
		res_text = re.subn('<style.*?</style>', '', res_text)[0]
		hxs = HtmlXPathSelector(text=res_text)
		
		try:
			tmp2 = hxs.select('//div[@class="BHbidSecBorderGrey"]')[0]
			tmp = tmp2.select('.//tr/td[@class="contentValueFont"]')[-1]
			Item['Posting_Datetime'] = ' '.join(tmp.select('.//text()').extract()).strip()
		except:
			pass
		return Item
		
			
	def parseItemDetails(self, response):
		try:
			signal.signal(signal.SIGALRM, self.handler)
			signal.alarm(10)
			item = self.parseItemDetailsTimeout(response)
			return item
		except:
			traceback.print_exc()
			return

	def handler(self, signum, frame):
		print "Parsing function taking forever!"
		raise Exception("end of time")

	def removeTags(self,element):
		try:
				element = str(element.encode('ascii','ignore'))
		except UnicodeError:
				element = str(element)
		except:
				element = str(element).encode('ascii','ignore')
		element = re.subn('<script .*?</script>', '', element)[0]
		element = re.subn('<style .*?</style>', '', element)[0]
		t=''
		s=element
		while s.find('<')>-1:
				i=0
				j=s.find('<')
				t+=s[i:j]
				i=s.find('>', j)+1
				#print i
				#print s
				s=s[i:]
				t+=' '
		t+=s
		t = re.subn(' +', ' ', t)[0]
		return t.strip()
