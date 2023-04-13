#!/usr/bin/python
# -*- coding: utf-8  -*-
# Check for consistency in commons category usage
# Mike Peel     08-Feb-2018      v1 - start
# Mike Peel     26-Mar-2018      Change recurse to 'False', shouldn't need to look in subcategories.

from __future__ import unicode_literals

import pywikibot
import numpy as np
import time
import string
from pywikibot import pagegenerators
import urllib

maxnum = 100000
nummodified = 0
# reportpage = 'User:Mike Peel/Commons redirects with Wikidata items'
skipto = 'Category:Austrobaileyaceae'
trap = 0

commons = pywikibot.Site('commons', 'commons')
repo = commons.data_repository()  # this is a DataSite object
# report = pywikibot.Page(commons, reportpage)
# if trap != 1:
#     report.text = ''
#     report.save('Blanking to restart logging')
debug = 1

targetcats = ['Category:Redirects connected to a Wikidata item', 'Category:Category redirects']

catredirect_templates = ["category redirect", "Category redirect", "seecat", "Seecat", "see cat", "See cat", "categoryredirect", "Categoryredirect", "catredirect", "Catredirect", "cat redirect", "Cat redirect", "catredir", "Catredir", "redirect category", "Redirect category", "cat-red", "Cat-red", "redirect cat", "Redirect cat", "category Redirect", "Category Redirect", "cat-redirect", "Cat-redirect", "Monotypic taxon category redirect", "monotypic taxon category redirect","Synonym taxon category redirect","mynonym taxon category redirect","Invalid taxon category redirect",'invalid taxon category redirect']
for targetcat in targetcats:
    print(targetcat)
    cat = pywikibot.Category(commons,targetcat)
    targets = cat.members(recurse=False);
    for target in targets:
        if trap == 1:
            if target.title() == skipto:
                trap = 0
            else:
                print(target.title())
            continue
        if 'Category:' in target.title():
            redirect = ''
            try:
                wd_item = pywikibot.ItemPage.fromPage(target)
                wd_item.get()
                print(wd_item.title())
            except:
                continue
            else:
                # We have a category that's linked to a Wikidata item, let's find out where it points.
                print(target.title())
                for option in catredirect_templates:
                    if "{{" + option in target.text:
                        try:
                            redirect = (target.text.split("{{" + option + "|"))[1].split("}}")[0].split("|")[0]
                        except:
                            try:
                                redirect = (target.text.split("{{" + option + " |"))[1].split("}}")[0].split("|")[0]
                            except:
                                try:
                                    redirect = target.text.split(f"{option} |")[1].split("}}")[0].split("|")[0]
                                except:
                                    print('Wikitext parsing bug!')
                        redirect = redirect.replace(u":Category:","")
                        redirect = redirect.replace(u"Category:","")
                if redirect:
                    # We have a redirect. Let's update its' commons sitelink on Wikidata.
                    print(redirect)
                    try:
                        data = {
                            'sitelinks': [
                                {
                                    'site': 'commonswiki',
                                    'title': f"Category:{redirect}",
                                }
                            ]
                        }
                        wd_item.editEntity(data, summary=u'Update commons sitelink to avoid commons category redirect')
                        nummodified += 1
                    except:
                        print("That didn't work!")
                        # report_text = report.get()
                        # report.text = report_text + "\n* [[:"+target.title()+"]] -> [[:Category:"+redirect+"]]\n"
                        # report.save('+1')

        if nummodified >= maxnum:
            print(f'Reached the maximum of {maxnum} entries modified, quitting!')
            exit()

print(f'Done! Edited {str(nummodified)} entries')
                
# EOF