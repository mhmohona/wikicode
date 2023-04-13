# License: MIT
import pywikibot
import re
import requests
import datetime

from pywikibot import pagegenerators

debug = False
maxnum = 5e9

checkedpages = []
reportpage = 'User:Mike Peel/Cochrane used'
pageschecked = []

site = pywikibot.Site('en', 'wikipedia')
report = pywikibot.Page(site, reportpage)

regexes = ["insource:/\| journal =.+Cochrane/", "insource:/\| journal=.+Cochrane/", "insource:/\|journal =.+Cochrane/", "insource:/\|journal=.+Cochrane/","insource:/\| title =.+Cochrane/", "title:/\| title=.+Cochrane/", "insource:/\|title =.+Cochrane/", "insource:/\|title=.+Cochrane/"]
i = 0
nummodified = 0

reporttext = "The following Cochrane review PMIDs (and probably other non-Cochrane PMIDs mixed in...) are used in Wikipedia articles:\n\n"
for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        # print checkedpages
        if page in pageschecked:
            continue

        print (page)
        pageschecked.append(page)
        i += 1
        try:
            text = page.get()
        except:
            continue
        pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
        print (len(pmids))
        for pmid in pmids:
            if f"* {str(pmid)} -" not in checkedpages:
                checkedpages.append(f"* {str(pmid)} - [[{page.title()}]]")
            else:
                index = [
                    idx
                    for idx, s in enumerate(checkedpages)
                    if f"* {str(pmid)} -" in s
                ][0]
                checkedpages[index] += f", [[{page.title()}]]"

        if len(checkedpages) > maxnum:
            print(f'Reached the maximum of {maxnum} pages loaded, saving!')
            break
    if len(checkedpages) > maxnum:
        print(f'Reached the maximum of {maxnum} pages loaded, saving!')
        break

print(f"{str(i)} pages checked, {len(checkedpages)} recorded!")
checkedpages.sort()
for checkedpage in checkedpages:
    reporttext += checkedpage + "\n"
report.text = reporttext
print (reporttext)
report.save('Update')
