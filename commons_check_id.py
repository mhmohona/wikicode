#!/usr/bin/python
# -*- coding: utf-8  -*-
# Migrate data from Commons to Wikidata
# Started 12 May 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 100000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = True
#category = 'Category:Cultural heritage monuments in Austria with known IDs'#'Category:Listed buildings in Wales with known IDs'#'Category:Listed buildings in England with known IDs'
#templates = ['Denkmalgeschütztes Objekt Österreich','denkmalgeschütztes Objekt Österreich', 'doo', 'Doo']#['Listed building Wales', 'listed building Wales']#['Listed building England', 'listed building England']
#properties = ['P2951']#['P1216', 'P1216']
# category = 'Category:Rijksmonumenten with known IDs'
# templates = ['Rijksmonument','rijksmonument',]
# properties = ['P359']
# shortname = 'Rijksmonument ID'
# category = 'Category:National Register of Historic Places with known IDs'
# templates = ['NRHP']
# properties = ['P649']
# shortname = 'NRHP ID'
# category = 'Category:National Register of Historic Places with known IDs'
# templates = ['Zabytek nieruchomy', 'zabytek nieruchomy']
# properties = ['P649']
# shortname = 'NRHP ID'
# category = 'Category:Mérimée ID without linked Wikidata'#'Category:Base Mérimée'
# templates = ['Mérimée', 'Merimee','mérimée', 'merimee']
# properties = ['P380']
# shortname = 'Mérimée ID'
category = 'Category:Protected areas with known WDPA-ID'#'Category:Base Mérimée'
templates = ['WDPA']
properties = ['P809']
shortname = 'WDPA ID'

def checkid(targetcat):
    print(targetcat)
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
    except:
        print("No Wikidata sitelink found")
        target_text = targetcat.get()

        id_val = 0
        for i in range(len(templates)):
            # try:
            #     value = (target_text.split("{{"+templates[i]+"|"))[1].split("|")[0]
            #     if value and id_val == 0:
            #         id_val = value
            # except:
            #     null = 1
                # print '1'
            # Special for Mirimee
            try:
                value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
                print(value)
                values = (value.split("|"))
                if "type" not in values[0]:
                    value = values[0]
                if "type" not in values[1]:
                    value = values[1]
                print(value)
                if value and id_val == 0:
                    id_val = value
            except:
                null = 1

            try:
                value = (target_text.split("{{"+templates[i]+" |1="))[1].split("}}")[0]
                if value and id_val == 0:
                    id_val = value
            except:
                null = 2
            try:
                value = (target_text.split("{{"+templates[i]+"|1="))[1].split("}}")[0]
                if value and id_val == 0:
                    id_val = value
            except:
                null = 3
            try:
                value = (target_text.split("{{"+templates[i]+"|"))[1].split("}}")[0]
                if value and id_val == 0:
                    id_val = value
            except:
                null = 1
        print(id_val)
        if id_val != 0:
            try:
                query = 'SELECT ?item WHERE { ?item wdt:'+str(properties[0])+' ?id . FILTER (?id = "'+str(id_val)+'") . } LIMIT 10'
                generator = pagegenerators.WikidataSPARQLPageGenerator(query, site=repo)
            except:
                print('Unable to run the query! Skipping this one.')
                time.sleep(3)
                return 0
            count = 0
            for testpage in generator:
                page = testpage
                count+=1
            print(count)
            if count == 1:
                try:
                    item_dict = page.get()
                    qid = page.title()
                except:
                    print('Huh - no page found')
                try:
                    sitelink = get_sitelink_title(item_dict['sitelinks']['commonswiki'])
                except:
                    # No existing sitelink found, add the new one
                    data = {'sitelinks': [{'site': 'commonswiki', 'title': targetcat.title()}]}
                    try:
                        print("\n\n")
                        print(qid)
                        print(id_val)
                        print(item_dict['labels'])
                        print(data)
                        # text = raw_input("Save? ")
                        # if text == 'y':
                        page.editEntity(data, summary=f'Add commons sitelink based on {shortname}')
                        return 1
                                            # else:
                                            #     return 0
                    except:
                        print('Edit failed')
                        return 0

                return 0

    return 0



# Start the category walker
# cat = pywikibot.Category(commons,category)
# nummodified += checkid(cat)
# targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

template = pywikibot.Page(commons, f'Template:{templates[0]}')

targetcats = template.embeddedin(namespaces='14')


for i, targetcat in enumerate(targetcats):
    # print targetcat
    # print "\n" + targetcat.title()
    # print target.text
    nummodified += checkid(targetcat)
    print(f"{str(nummodified)}/{str(i)}")
    if nummodified >= maxnum:
        print(f'Reached the maximum of {str(maxnum)} entries modified, quitting!')
        exit()

print(f'Done! Edited {str(nummodified)} entries')
                
# EOF