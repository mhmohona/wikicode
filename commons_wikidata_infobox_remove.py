#!/usr/bin/python
# -*- coding: utf-8  -*-
# Remove unneeded calls to Wikidata infoboxes on Commons
# Started 21 June 2018 by Mike Peel
from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib
from pibot_functions import *

maxnum = 1000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = True
manual = True
templates = ['AirDisasters','Finlandyear', 'Finlandyear-Sweden']
others = ['mainw','Mainw', 'Interwiki from Wikidata', 'interwiki from Wikidata', 'label', 'Label', 'object location|wikidata=', 'object location|Wikidata=', 'Object location|Wikidata=', 'Object location|wikidata=', "Interwiki from Wikidata", "interwiki from Wikidata", "Interwiki from wikidata", "interwiki from wikidata", "PeopleByName", "peopleByName", "Authority control", "authority control", "On Wikidata", "on Wikidata", "In Wikidata", "in Wikidata", "Wikidata", "wikidata", "en"]
enwp = ['mainw', 'Mainw', 'on Wikipedia|en=', 'On Wikipedia|en=']
savemessage="Removing Wikidata Infobox as it is included in Finlandyear"
wikidatainfobox = ["Wikidata Infobox", "Wikidata infobox", "wikidata infobox", "wikidata Infobox", "Infobox Wikidata", "infobox Wikidata", "infobox wikidata", "Infobox wikidata", "Wikidata  infobox", "wikidata  infobox"]

def migratecat(targetcat):
    print (targetcat)
    target_text = targetcat.get()
    print (target_text)
    # Check that we have a Wikidata infobox here
    if not any(option in target_text for option in wikidatainfobox):
        print ('No infobox')
        return 0

    # Fetch the info from Wikidata
    try:
        wd_item = pywikibot.ItemPage.fromPage(targetcat)
        item_dict = wd_item.get()
        print (wd_item.title())
    except:
        print ('No Wikidata ID')
        return 0

    # Or in the main topic
    wd_item2 = 0
    try:
        p301 = item_dict['claims']['P301']
        for clm2 in p301:
            wd_item2 = clm2.getTarget()
            item_dict = wd_item.get()
    except:
        null = 1

    # Remove other templates
    for i in range(0,len(others)):
        target_text = target_text.replace("{{"+others[i]+"}}", "")
        target_text = target_text.replace("{{" + others[i] + "|" + wd_item.title() + "}}", "")
        target_text = target_text.replace("{{" + others[i] + "|Wikidata=" + wd_item.title() + "}}", "")
        target_text = target_text.replace("{{" + others[i] + "|wikidata=" + wd_item.title() + "}}", "")
        target_text = target_text.replace("{{" + others[i] + wd_item.title() + "}}", "")
        target_text = target_text.replace("{{" + others[i] + "| }}", "")
        target_text = target_text.replace("{{" + others[i] + " | }}", "")

    try:
        enwp_link = get_sitelink_title(item_dict['sitelinks']['enwiki'])
        enwp_link2 = enwp_link[0].lower() + enwp_link[1:]
        for i in range(0,len(enwp)):
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link+"}}", "")
            target_text = target_text.replace("{{"+enwp[i]+"|"+enwp_link2+"}}", "")
    except:
        null = 1

    for i in range(0,len(wikidatainfobox)):
        target_text = target_text.replace("{{"+wikidatainfobox[i]+"|"+wd_item.title(),'{{Wikidata Infobox')
        target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid="+wd_item.title(),'{{Wikidata Infobox')
        if wd_item2 != 0:
            target_text = target_text.replace("{{"+wikidatainfobox[i]+"|"+wd_item2.title(),'{{Wikidata Infobox')
            target_text = target_text.replace("{{"+wikidatainfobox[i]+"|qid="+wd_item2.title(),'{{Wikidata Infobox')
        target_text = target_text.replace("{{"+wikidatainfobox[i],'{{Wikidata Infobox')

    lines = target_text.splitlines()
    insertline = 0
    i = 0
    j = 0
    for line in lines:
        if '{{Wikidata Infobox}}' in line:
            i += 1
            # if i != 1:
            lines[j] = lines[j].replace('{{Wikidata Infobox}}', '')
        j += 1
    target_text = "\n".join(lines)

    # Only remove whitespace if we're making another change
    if (target_text != targetcat.get()):
        target_text = target_text.replace('\n\n\n','\n')
        target_text = target_text.replace('\n\n\n','\n')
        target_text = target_text.replace('\n\n{{Wikidata Infobox','\n{{Wikidata Infobox')
        # target_text = target_text.replace('\n\n','\n')

    # Time to save it
    if (target_text != targetcat.get()):
        targetcat.text = target_text.strip()
        print (targetcat.text)
        if manual:
            text = raw_input("Save on Commons? ")
            if text == '':
                try:
                    targetcat.save(savemessage)
                    return 1
                except:
                    print ("That didn't work!")
                    return 0
            else:
                return 0
        else:
            try:
                targetcat.save(savemessage)
                return 1
            except:
                print ("That didn't work!")
                return 0
    else:
        return 0

for i in range(0,len(templates)):
    template = pywikibot.Page(commons, 'Template:'+templates[i])
    targetcats = template.embeddedin(namespaces='14')

    for targetcat in targetcats:
        print (targetcat)
        print ("\n" + targetcat.title())
        nummodified += migratecat(targetcat)

        if nummodified >= maxnum:
            print ('Reached the maximum of ' + str(maxnum) + ' entries modified, quitting!')
            exit()

    print ('Done! Edited ' + str(nummodified) + ' entries')
                    
# EOF
