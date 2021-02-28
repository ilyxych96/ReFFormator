#  -*- coding: utf-8 -*-
import requests, json
from bs4 import BeautifulSoup as BS
import re

'''

1) Parser test:  
    Check journal in each publishers
    
2) Solve Elsevir problem (don't work double redirect from doi)

'''

newNamesFormat = ['SURNAME', 'NAME', 'SECNAME']  # input form user
newformat = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PAGERANGE', 'DOI']  # input form user

delimiterItems = '; '  # input form user
delimiterNames = ', '  # input form user


def parser(URL):
    """                        Parser out mask
            [ NAMES=[NAME, SECNAME, SURNAME], TITLE, JOURNAL, YEAR, VOLUME, ISSUE, PAGERANGE, DOI ]
    """

    def get_html(URL, params=None):
        headers = {
            'Accept': 'application/rdf+xml;q=0.5, application/vnd.citationstyles.csl+json;q=1.0',
        }
        response = requests.get(URL, headers=headers, params=params, allow_redirects=True)
        return response

    json_data = json.loads(get_html(URL).text)

    article_information = []
    names = []
    for author in json_data['author']:
        current_author = []
        surname = author['family']
        name = author['given']
        try:
            name, second_name = name.split(' ')
        except:
            second_name = '-'
        current_author.append(name)
        current_author.append(second_name)
        current_author.append(surname)
        names.append(current_author)

    try:
        title = json_data['title']
    except:
        title = 'None'
    try:
        journal = json_data['container-title']
    except:
        journal = 'None'
    try:
        journal_short = json_data['container-title-short']
    except:
        journal_short = 'None'
    try:
        year = str(json_data['indexed']['date-parts'][0][0])
    except:
        year = 'None'
    try:
        volume = json_data['volume']
    except:
        volume = 'None'
    try:
        issue = json_data['issue']
    except:
        issue = 'None'
    try:
        pages = json_data['page']
    except:
        pages = 'None'
    try:
        doi = json_data['DOI']
    except:
        doi = 'None'

    article_information.append(names)
    article_information.append(title)
    article_information.append(journal_short)
    article_information.append(year)
    article_information.append(volume)
    article_information.append(issue)
    article_information.append(pages)
    article_information.append(doi)

    return article_information


def referenceOrderEditor(reference, refNamesFormat, referenceFormat):
    '''
    Function formatting parsed information to new style

    OUTPUT: Reformatting reference_list
    '''
    tags = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PAGERANGE', 'DOI']
    #referenceDict = dict(zip(tags, reference))
    print(reference)
    referenceNewform = []
    names = []
    secnames = []
    surnames = []
    authors = []
    for name in reference[referenceFormat[0]]:
        names.append(name[0])
        secnames.append(name[1])
        surnames.append(name[2])

    authors.append(names)
    authors.append(secnames)
    authors.append(surnames)
    oldrefNamesFormat = ['NAME', 'SECNAME', 'SURNAME']
    namesDict = dict(zip(oldrefNamesFormat, authors))

    names = []
    sortNames = []
    for i in range(len(namesDict[refNamesFormat[0]])):
        names.append(namesDict[refNamesFormat[0]][i])
        names.append(namesDict[refNamesFormat[1]][i])
        names.append(namesDict[refNamesFormat[2]][i])
        sortNames.append(names)
        names = []

    referenceNewform.append(sortNames)
    for item in referenceFormat[1:]:
        referenceNewform.append(reference[item])

    return referenceNewform


def ref_to_string(reference):
    # SCRIPT:
    string = ''
    for name in reference[0]:
        for item in name:
            if item == '-':
                continue
            else:
                string += item + ' '
        string = string[:-1] + delimiterNames

    string = string[:-len(delimiterNames)] + delimiterItems

    for item in reference[1:]:
        string += str(item) + delimiterItems

    string += '\n'
    return string


def startparser(sourcefile, newNamesFormat, newformat):
    source_file = open(sourcefile, 'r')
    for doi in source_file:
        item = doi.split('/')
        if item[0] == 'https:':
            doi = doi
        elif item[0] == 'doi.org':
            doi = 'https:/'
            for element in item:
                doi += '/' + str(element)
        elif 'DOI: ' or 'DOI:' or 'doi: ' or 'doi:' in doi:
            doitmp = 'https://doi.org/'
            doitmp += doi
            doi = doitmp
        else:
            doi = 'https://doi.org/'
            for element in item:
                doi += '/' + str(element)

        try:
            ref = parser(doi)
            tags = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PAGERANGE', 'DOI']
            tagsDict = dict(zip(tags, ref))
        except:
            continue

        ref = referenceOrderEditor(tagsDict, newNamesFormat, newformat)
        ref = ref_to_string(ref)
        print(ref)



testmode = 0
if testmode == 1:
    print('Debug mode')
    URL = 'https://doi.org/10.1021/acs.chemmater.9b03963'
    tmpref = parser(URL)
    print(referenceOrderEditor(tmpref, newNamesFormat, newformat))
#else:
#    print('File mode')
#    #sourcefile = r'C:\Users\ilya_\Documents\GitHub\ReFFormator\articles_information.txt'
#    startparser(sourcefile, newNamesFormat, newformat)


