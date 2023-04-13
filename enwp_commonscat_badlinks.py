#!/usr/bin/python
# -*- coding: utf-8  -*-
# Change locally defined commons category links to the Wikidata one
# Mike Peel     10-Sep-2019      v1 - start

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *
import random
# import mysql.connector
# from database_login import *

# mydb = mysql.connector.connect(
#   host=database_host,
#   user=database_user,
#   passwd=database_password,
#   database=database_database
# )
# mycursor = mydb.cursor()

maxnum = 100000
nummodified = 0

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()  # this is a DataSite object
commons = pywikibot.Site('commons', 'commons')
enwp = pywikibot.Site('en', 'wikipedia')
enwp_site = 'enwiki'
prefix = 'en'
# enwp = pywikibot.Site('simple', 'wikipedia')
# enwp_site = 'simplewiki'
# prefix = 'simple'
debug = 1
trip = 1
trip_next = 0
only_replacements = False
check_sitelink = True
templates = ['commonscat', 'Commonscat', 'commonscategory', 'Commonscategory', 'commons category', 'Commons category', 'commons cat', 'Commons cat', 'Commons category-inline', 'commons category-inline', 'Commons cat-inline', 'commons cat-inline', 'commonscat-inline', 'Commonscat-inline', 'Commons category inline', 'commons category inline', 'commons-cat-inline', 'Commons-cat-inline', 'Commons cat inline', 'commons cat inline', 'commonscat inline', 'Commonscat inline', 'Commons Category', 'commons Category','commonscatinline', 'Commonscatinline']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect"]

targetcats = ['Category:Commons category link is defined as the pagename','Commons category link is locally defined','Category:Commons category link is on Wikidata using P373']
skip_rest = False
# targetcats = ['Commons category link is locally defined']

for targetcat in targetcats:
	for category in np.arange(0,2):
		cat = pywikibot.Category(enwp, targetcat)
		if category == 0:
			pages = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);
		else:
			pages = pagegenerators.CategorizedPageGenerator(cat, recurse=False);
		for page in pages:
			print('')
			print('https://en.wikipedia.org/wiki/'+page.title().replace(' ','_'))
			if trip_next:
				trip = 1
				trip_next = 0
			# Optional skip-ahead to resume broken runs
			if trip == 0:
				if "List of New Jersey state parks" in page.title():
					trip_next = 1
				else:
					print(page.title())
				continue
			# Get the Wikidata item
			has_item = True
			try:
				wd_item = pywikibot.ItemPage.fromPage(page)
				item_dict = wd_item.get()
				qid = wd_item.title()
				print(qid)
			except:
				# If that didn't work, go no further
				print(f'{page.title()} - no page found')
				has_item = False
			if not has_item:
				print('No item')
				continue

			print('b')
			sitelink = False
			try:
				sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
			except:
				null = 0
			# Switch to category item?
			p910_followed = False
			try:
				existing_id = item_dict['claims']['P910']
				print('P910 exists, following that.')
				for clm2 in existing_id:
					wd_item = clm2.getTarget()
					item_dict = wd_item.get()
					qid = wd_item.title()
					print(wd_item.title())
					p910_followed = True
			except:
				null = 0
			if sitelink and p910_followed and 'Category' in sitelink:
				input('Has sitelink in main item, check?')
			try:
				sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
			except:
				sitelink = False
				null = 0

			if sitelink and 'Category:' not in sitelink:
				input('Check, sitelink is not to a category')
				continue
			if not sitelink:
				print('No sitelink')
			else:
				print('Has sitelink')

print(f'Done! Edited {nummodified} entries')

# EOF
