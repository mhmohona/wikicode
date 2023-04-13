#!/usr/bin/python
# -*- coding: utf-8  -*-
# License: MIT
import pywikibot
import re
import requests
import datetime
import locale

from pywikibot import pagegenerators

debug = False
maxnum = 1000
reportpage = u'Projet:Médecine/Cochrane/Bot'
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

def update_report(page, old_pmid, new_pmid, previousreports):
    report = pywikibot.Page(site, reportpage)
    report_text = report.get()
    rep = u'Article [[%s]] ([{{fullurl:%s|action=edit}} edit]) ancienne critique [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s] nouvelle critique [https://www.ncbi.nlm.nih.gov/pubmed/%s PMID:%s]' % (page.title(), page.title(),old_pmid, old_pmid, new_pmid, new_pmid)
    if rep in report_text or rep in previousreports:
        return
    report.text = report_text + "\n*" + rep + u' - ~~~~~'
    report.save(f'Rapport de mise à jour à inclure {page.title()}')

checkedpages = {}

site = pywikibot.Site('fr', 'wikipedia')

# First clean up the report page
report = pywikibot.Page(site, reportpage)
report_text = report.get()
report_text = report_text.splitlines()
archive = pywikibot.Page(site, f"{reportpage}/Archiver")
archive_text = archive.get()
report_text_new = ''
# print(report_text)
for line in report_text:
    print(line)
    # exit()
    if "{{Fait" in line or "{{fait" in line:
        archive_text = archive_text + "\n" + line
    else:
        report_text_new = report_text_new + "\n" + line
print(report_text_new)
print(archive_text)
if debug == False:
    archive.text = archive_text.strip()
    archive.save("Archivage d'anciens rapports")
    report.text = report_text_new.strip()
    report.save("Archivage d'anciens rapports")

previousreports = archive_text + "\n" + report_text_new
regexes = ["insource:/\| périodique =.+Cochrane/", "insource:/\| périodique=.+Cochrane/", "insource:/\|périodique =.+Cochrane/", "insource:/\|périodique=.+Cochrane/","insource:/\| titre =.+Cochrane/", "titre:/\| title=.+Cochrane/", "insource:/\|titre =.+Cochrane/", "insource:/\|titre=.+Cochrane/"]
i = 0
nummodified = 0

todaysdate = datetime.datetime.now()
todaysdate.strftime("%B")
datestr = "|date = " + (todaysdate.strftime("%B %Y")).lower()
print(datestr)

for regex in regexes:
    generator = pagegenerators.SearchPageGenerator(regex, site=site, namespaces=[0])
    gen = pagegenerators.PreloadingGenerator(generator)

    for page in gen:
        # print(checkedpages)
        # print(page)
        # page = pywikibot.Page(site, "Alzheimer's disease")
        i += 1
        try:
            text = page.get()
        except:
            continue
        pmids = re.findall(r'\|\s*?pmid\s*?\=\s*?(\d+?)\s*?\|', text)
        print(len(pmids))
        for pmid in pmids:
            if str(pmid) not in checkedpages:
                print(f'https://pubmed.ncbi.nlm.nih.gov/{pmid}')
                try:
                    r = requests.get(f'https://pubmed.ncbi.nlm.nih.gov/{pmid}', timeout=10.0)
                    res = r.text
                except:
                    continue
                # if 'WITHDRAWN' in res and re.search(r'<h3>Update in</h3><ul><li class="comments"><a href="/pubmed/\d+?"', res):
                rawtext = re.sub(r'\s+', '', res)
                if re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext):
                    pm = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext)[0]
                    print(pm)
                    checkedpages[str(pmid)] = pm
                    # Check to make sure that the new paper doesn't also have an updated version...
                    try:
                        r2 = requests.get(f'https://pubmed.ncbi.nlm.nih.gov/{pm}', timeout=10.0)
                        res2 = r2.text
                    except:
                        continue
                    if '<title>WITHDRAWN' in res2:
                        # The new one's been withdrawn: we don't want to report this as an update.
                        checkedpages[str(pmid)] = 0
                    rawtext2 = re.sub(r'\s+', '', res2)
                    if 'WITHDRAWN' in res2 and re.search(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2):
                        pm2 = re.findall(r'data-ga-category="comment_correction"data-ga-action="(\d+?)"data-ga-label="linked-update">', rawtext2)[0]
                        try:
                            r3 = requests.get(f'https://pubmed.ncbi.nlm.nih.gov/{pm2}', timeout=10.0)
                            res3 = r3.text
                            checkedpages[str(pmid)] = 0 if '<title>WITHDRAWN' in res3 else pm2
                        except:
                            continue
                else:
                    checkedpages[str(pmid)] = 0
            else:
                print(f'using cache for {str(pmid)}')
            print(checkedpages[str(pmid)])
            if (
                checkedpages[str(pmid)] != 0
                and f'<!-- Aucune mise à jour nécessaire: {str(pmid)} -->'
                not in text
            ):
                up = (
                    f'<!-- Nouvelle revue https://pubmed.ncbi.nlm.nih.gov/{checkedpages[str(pmid)]}'
                    + u" -->{{Passage à actualiser"
                )
                if up not in text and debug == False:
                    update_report(page, pmid, checkedpages[str(pmid)], previousreports)
                    nummodified += 1
        if nummodified > maxnum - 1:
            print(f'Reached the maximum of {str(maxnum)} pages modified, quitting!')
            exit()

print(f"{str(i)} pages checked, {str(nummodified)} tagged!")


# if text != page.text and debug == False:
#     page.text = text
#     page.save(u'ajout d\'un modèle de passage à actualiser pour la référence Cochrane')
#     nummodified += 1
#     if nummodified > maxnum - 1:
#         print('Reached the maximum of ' + str(maxnum) + ' pages modified, quitting!')
#         exit()
