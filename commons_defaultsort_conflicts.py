#!/usr/bin/python3
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     18-Apr-2018      v1 - start
# Mike Peel     17 Oct 2020      Update to python3

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 10000
nummodified = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
debug = 1
manual = 0
savemessage = "Disable defaultsort from infobox to avoid conflict"

def fixcat(targetcat):
    target_text = targetcat.get()
    target_text = target_text.replace("{{Wikidata Infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{Wikidata infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{wikidata Infobox}}", "{{Wikidata Infobox|defaultsort=no}}")
    target_text = target_text.replace("{{wikidata infobox}}", "{{Wikidata Infobox|defaultsort=no}}")

    if target_text == targetcat.get():
        return 0
    print(target_text)
    targetcat.text = target_text.strip()
    if manual == 1:
        text = raw_input("Save on Commons? ")
        if text != 'y':
            return 0
    try:
        targetcat.save(savemessage)
        return 1
    except:
        print("That didn't work!")
        return 0


startcat = 'Category:Pages with DEFAULTSORT conflicts'

# First touch the pages to make sure it's not a caching issue
cat = pywikibot.Category(commons,startcat)
for result in pagegenerators.SubCategoriesPageGenerator(cat, recurse=False):
    result.touch()

# Then disable the defaultsort if still needed.
cat = pywikibot.Category(commons,startcat)
targetcats = pagegenerators.SubCategoriesPageGenerator(cat, recurse=False);

for targetcat in targetcats:
    print(targetcat)
    print("\n" + targetcat.title())
    # print(target.text)
    nummodified += fixcat(targetcat)

    if nummodified >= maxnum:
        print(f'Reached the maximum of {str(maxnum)} entries modified, quitting!')
        exit()

print(f'Done! Edited {str(nummodified)} entries')
                
# EOF