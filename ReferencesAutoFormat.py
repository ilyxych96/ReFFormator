#  -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as BS
import re

'''

1) Parser test:  
    Check journal in each publishers
    
2) Solve Elsevir problem (don't work double redirect from doi)

'''
#NamesFormat = ['SURNAME', 'NAME', 'SECNAME']  # input form user
#format = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PageRange', 'DOI']  # input form user
# INPUTS:
#sourcefile = 'articles.txt'  # input form user
newNamesFormat = ['SURNAME', 'NAME', 'SECNAME']  # input form user
newformat = ['NAMES', 'YEAR', 'VOLUME', 'ISSUE', 'PAGERANGE', 'DOI']  # input form user

delimiterItems = '; '
delimiterNames = ', '


def parser(URL):
    """                        Parser out mask
        [ NAMES=[NAME, SECNAME, SURNAME], TITLE, JOURNAL, YEAR, VOLUME, ISSUE, PageRange, DOI ]
    """

    def get_html(URL, params=None):
        headers = []
        response = requests.get(URL, headers=headers, params=params, allow_redirects=True)
        return response

    def get_data_RSC(html):
        """
        Errors:

        """
        soup = BS(html, 'html.parser')
        names = soup.findAll(class_='input__checkbox')
        information = []
        authors = []
        # get authors
        for author in names:
            items = author.get_text(strip=True).split(' ')
            if len(items) == 2:
                items.insert(1, '-')
            authors.append(items)

        information.append(authors)
        # get title
        tmp = soup.findAll(class_='capsule__title fixpadv--m')
        for item in tmp:
            title = item.get_text()[4:]
        title = title.split()
        string = ''
        for word in title:
            string += str(word) + ' '
        title = string[:-1]

        # get article info
        items = soup.findAll(class_='c__14')
        count = 0
        for item in items:
            if count == 3:
                line = str(item.get_text(strip=True))
                about = line.split(',')
            count += 1

        # get issue
        tmp = soup.findAll(class_='article-nav__issue autopad--h')
        for item in tmp:
            item = str(item.get_text())

        issue = item.split(',')[0].split()[1]
        journal = about[0]
        year = about.pop(1)
        year = year.split()
        about.insert(1, year[0])
        volume = about[2]

        # sort data
        pageRangeTmp = str(about[-1:])
        pageRange = ''
        about.pop(len(about) - 1)
        truelist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-']
        for symbol in pageRangeTmp:
            if symbol in truelist:
                pageRange += symbol
        about.append(issue)
        about.append(pageRange)
        information.append(title)
        information.extend(about)

        # get DOI
        doi = soup.find(class_='doi-link').get_text()[1:-1]
        information.append(doi)

        return information

    def get_data_ACS(html):

        '''
        Errors:
        Some journals have different authors link
        direct link: https://doi.org/10.1021/acsami.8b07554
        in <a href>: https://doi.org/10.1021/acscentsci.7b00572
        '''

        about = []
        authors = []
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='loa-info-name')
        for item in names:
            item = item.get_text().split(' ')
            if len(item) == 2:
                item.insert(1, '-')
            authors.append(item)

        about.append(authors)
        title = soup.find(class_='hlFld-Title').get_text()
        journal = soup.find('span', class_='cit-title').get_text()
        year = soup.find('span', class_='cit-year-info').get_text()
        volumetmp = soup.find('span', class_='cit-volume').get_text()
        issuetmp = soup.find('span', class_='cit-issue').get_text()
        pageRangetmp = soup.find('span', class_='cit-pageRange').get_text()
        doi = soup.find(class_='article_header-doiurl').find('a').get_text()

        volume = ''
        for symbol in volumetmp:
            if symbol.isdigit() or symbol == '-':
                volume += symbol

        issue = ''
        for symbol in issuetmp:
            if symbol.isdigit() or symbol == '-':
                issue += symbol

        pageRange = ''
        for symbol in pageRangetmp:
            if symbol.isdigit() or symbol == '–':
                pageRange += symbol

        about.append(title)
        about.append(journal)
        about.append(year)
        about.append(volume)
        about.append(issue)
        about.append(pageRange)
        about.append(doi)

        return about

    def get_data_Elsevir(html):
        '''
        Errors:

        '''
        information = []
        tmpauthors = []
        authors = []
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='text given-name')
        surnames = soup.find_all(class_='text surname')
        for i in range(len(names)):
            tmpauthors.append(str(names[i].get_text()) + ' ' + str(surnames[i].get_text()))

        for name in tmpauthors:
            name = name.split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)

        information.append(authors)
        title = soup.find(class_='title-text')
        information.append(title.get_text())
        journal = soup.find(class_='publication-title-link')
        information.append(journal.get_text())
        VolYearPage = soup.find(class_='text-xs')
        issue = '-'
        try:
            volumetmp, yeartmp, pageRangetmp = str(VolYearPage.get_text()).split(', ')
        except:
            volumetmp, issuetmp, yeartmp, pageRangetmp = str(VolYearPage.get_text()).split(', ')
        volume = ''
        issue = ''
        year = ''
        pageRange = ''

        for symbol in yeartmp:
            if symbol.isdigit():
                year += symbol

        for symbol in volumetmp:
            if symbol.isdigit() or symbol == '-':
                volume += symbol

        for symbol in issuetmp:
            if symbol.isdigit() or symbol == '–':
                issue += symbol

        for symbol in pageRangetmp:
            if symbol.isdigit() or symbol == '-':
                pageRange += symbol

        information.append(year)
        information.append(volume)
        information.append(issue)
        information.append(pageRange)

        # get DOI
        doi = soup.find(class_='DoiLink')
        information.append(doi.get_text().split('(')[0])

        return information

    def get_data_Springer(html):
        '''
        Errors:

        '''
        information = []
        authors = []
        soup = BS(html, 'html.parser')
        # get names
        names = soup.find_all(class_='c-author-list__item')
        for name in names:
            name = name.get_text()[:-2].rstrip(' ').split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)
        information.append(authors)

        title = soup.find(class_='c-article-title')
        information.append(title.get_text())

        info = soup.find(class_='c-article-info-details')
        issue = soup.find(attrs={"name": re.compile(r"issue", re.I)})
        issue = issue['content']
        tmp, trash = info.get_text().split('(')
        year, trash = trash.split(')')
        tmp, pages = tmp.split('pages')
        journal, volume = tmp.split('volume')
        information.append(journal[1:-2])
        information.append(year)
        volume = volume[1:-2]
        information.append(volume)
        information.append(issue)
        information.append(pages)

        # get DOI
        data = soup.findAll(class_='c-bibliographic-information__value')
        information.append(data[len(data) - 1].get_text())

        return information

    def get_data_Nature(html):
        '''
        Errors:

        '''
        information = []
        authors = []
        tmpauthors = []
        wronglist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '&']
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='c-author-list__item')
        filterauthor = ''
        for name in names:
            author = name.get_text()
            for letter in str(author):
                if letter not in wronglist:
                    filterauthor += str(letter)
            tmpauthors.append(filterauthor.rstrip())
            filterauthor = ''
            for name in tmpauthors:
                name = name.split(' ')
                if len(name) == 2:
                    name.insert(1, '-')
                authors.append(name)

        information.append(authors)
        title = soup.find(class_='c-article-title')
        information.append(title.get_text())

        info = soup.find(class_='c-article-info-details')
        tmp, trash = info.get_text().split('(')
        year, trash = trash.split(')')
        tmp, issue = tmp.split(', Article number: ')
        journal, volume = tmp.split('volume ')
        information.append(journal[1:-2])
        information.append(year)
        information.append(volume)
        information.append(issue[:-1])
        pageRange = '???'
        information.append(pageRange)

        # get DOI
        doi = soup.find(class_='c-bibliographic-information__citation')
        information.append(str(doi.get_text()).split('). ')[1])

        return information

    def get_data_Wiley(html):  # outs format!
        '''
        Errors:

        '''
        information = []
        authors = []
        altlinks = []
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='author-name accordion-tabbed__control')
        for name in names[:len(names) // 2]:
            name = name.get_text().split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)

        information.append(authors)
        title = soup.find(class_='citation__title')

        imglinks = soup.find_all('img', alt=True)
        for x in imglinks:
            altlinks.append(x.get('alt'))  # adding into list
        journal = altlinks[2]

        # get year
        year = soup.find(class_='epub-date').get_text()

        day, month, year = year.split(' ')

        # get volume issue
        VolumeIssue = soup.find(class_='volume-issue')
        volumetmp, issuetmp = str(VolumeIssue.get_text()).split(', ')

        volume = ''
        for symbol in volumetmp:
            if symbol.isdigit() or symbol == '-':
                volume += symbol

        issue = ''
        for symbol in issuetmp:
            if symbol.isdigit() or symbol == '-':
                issue += symbol

        # get PageRange
        PageRangetmp = soup.find_all(class_='page-range')
        for item in PageRangetmp:
            if 'Pages' in item.get_text():
                PageRangetmp = item.get_text()

        PageRange = ''
        for symbol in PageRangetmp:
            if symbol.isdigit() or symbol == '-':
                PageRange += symbol

        doi = soup.find(class_='epub-doi').get_text()

        information.append(title.get_text())
        information.append(journal)
        information.append(year)
        information.append(volume)
        information.append(issue)
        information.append(PageRange)
        information.append(doi)

        return information

    def get_data_Science(html):
        '''
        Errors:

        '''
        information = []
        authors = []
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='name')
        for name in names:
            name = name.get_text().split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)
        information.append(authors)

        title = soup.find(class_='highwire-cite-title')
        tmp = soup.find(class_='meta-line')
        tmp, doi = tmp.get_text().split('DOI: ')
        tmp, issuebroken, pagebroken = tmp.split(', ')
        page = ''
        issue = ''
        for letter in pagebroken:
            if letter.isdigit() or letter == '-':
                page += letter

        for letter in issuebroken:
            if letter.isdigit():
                issue += letter

        tmp, volume = tmp.split(':Vol. ')
        lst = tmp.split()
        year = lst[-1]
        del lst[-1]
        month = lst[-1]
        del lst[-1]
        day = lst[-1]
        del lst[-1]
        date = day + ' ' + month + ' ' + year
        journal = ''
        for item in lst:
            journal += item + ' '

        doi = 'https://' + doi.rstrip()
        information.append(title.get_text())
        information.append(journal[:-1])
        information.append(year)
        information.append(volume)
        information.append(issue)
        information.append(page)
        information.append(doi)

        return information

    def get_data_AIP(html):
        '''
        Errors:

        '''
        information = []
        tmpauthors = []
        authors = []
        soup = BS(html, 'html.parser')
        names = soup.find_all(class_='contrib-author')
        breaksymbols = [',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for nametmp in names:
            nametmp = nametmp.get_text().rstrip().lstrip()
            name = ''
            for symbol in str(nametmp):
                if symbol in breaksymbols:
                    break
                elif symbol == ')':
                    name = name[:-1]
                else:
                    name += symbol

            tmpauthors.append(name)

        for name in tmpauthors:
            name = name.split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)
        information.append(authors)

        title = soup.find(class_='publicationContentTitle')
        information.append(title.get_text().lstrip().rstrip())

        journal = soup.find(class_='header-journal-title')
        information.append(journal.get_text())

        tmp = soup.find(class_='publicationContentCitation')
        tmp = tmp.get_text()

        tmp, doi = tmp.split(';')
        doi = doi.rstrip().lstrip()

        tmp, page_year = tmp.split(',')
        page, yeartmp = page_year.split(' (')
        year = ''
        for symbol in yeartmp:
            if symbol.isdigit():
                year += symbol

        tmp = soup.find(class_='breadcrumbs')
        tmp = tmp.get_text().split('>')
        tmp = str(tmp[-2:-1])
        volume, issuetmp = tmp.split(', ')
        tmp, volume = volume.split('Volume ')
        issue = ''
        for symbol in issuetmp:
            if symbol.isdigit():
                issue += symbol

        information.append(year)
        information.append(volume)
        information.append(issue)
        information.append(page.lstrip())
        information.append(doi)

        return information

    def get_data_tandf(html):
        '''
        Errors:

        '''
        information = []
        soup = BS(html, 'html.parser')
        names = soup.find(class_='authors').get_text()
        names = names.replace(' &', ',')
        try:
            names = names.split(', ')
        except:
            names = names

        authors = []
        for name in names:
            name = name.split(' ')
            if len(name) == 2:
                name.insert(1, '-')
            authors.append(name)
        information.append(authors)
        title = soup.find(class_='NLM_article-title hlFld-title')
        information.append(title.get_text())

        tmp = soup.find(class_='title-container').get_text()
        tmp, issue = tmp.split(' - Issue ')
        issue = str(issue).rstrip().lstrip()
        tmp, year = tmp.split(', ')
        tmp, volume = tmp.split('Volume ')

        jrnl = tmp.split()[1:]
        journal = ''
        for word in jrnl:
            journal += word + ' '

        journal = journal[:-1]

        pages = soup.findAll(class_='inline-dropzone')
        pages, doi = pages[2].get_text().split('Download citation')
        doi, trash = doi.split('CrossMark')

        pages = pages.split('Received')[0]
        pages = str(pages).rstrip().lstrip().split(' ')[1]

        information.append(journal)
        information.append(year)
        information.append(volume)
        information.append(issue)
        information.append(pages)
        information.append(str(doi).rstrip().lstrip())

        return information

    def classification(URL, html_text):
        domen = URL.split('/')[2]
        if domen == 'pubs.acs.org':
            print('ACS: ')
            information = get_data_ACS(html_text)
        elif domen == 'pubs.rsc.org':
            print('RCS: ')
            information = get_data_RSC(html_text)
        elif domen == 'www.sciencedirect.com':
            print('Elsevir: ')
            information = get_data_Elsevir(html_text)
        elif domen == 'link.springer.com':
            print('Springer: ')
            information = get_data_Springer(html_text)
        elif domen == 'www.nature.com':
            print('Nature: ')
            information = get_data_Nature(html_text)
        elif domen == 'onlinelibrary.wiley.com':
            print('Wiley: ')
            information = get_data_Wiley(html_text)
        elif '.sciencemag.' in domen:
            print('Science: ')
            information = get_data_Science(html_text)
        elif domen == 'aip.scitation.org':
            print('AIP: ')
            information = get_data_AIP(html_text)
        elif 'tandfonline.com' in domen:
            print('TandF: ')
            information = get_data_tandf(html_text)

        try:
            return information
        except:
            return URL

    try:
        html = get_html(URL)
        if html.status_code == 200:
            information = classification(html.url, html.text)
            print(information)
        # temporary check else. must be remove
        else:
            information = URL
            print('Error: ', URL)
    except:
        information = ''

    return information


def referenceOrderEditor(reference, refNamesFormat, referenceFormat):
    '''
    Function formatting parsed information to new style

    OUTPUT: Reformatting reference_list
    '''
    tags = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PAGERANGE', 'DOI']
    referenceDict = dict(zip(tags, reference))
    referenceNewform = []
    names = []
    secnames = []
    surnames = []
    authors = []
    for name in referenceDict[referenceFormat[0]]:
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
        referenceNewform.append(referenceDict[item])

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
    print('File source mode')
    source_file = open(sourcefile, 'r')
    outfile = sourcefile.split('.')
    f = open(outfile[0] + '_information.' + outfile[1], 'w+', encoding='utf-8')
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
            tags = ['NAMES', 'TITLE', 'JOURNAL', 'YEAR', 'VOLUME', 'ISSUE', 'PageRange', 'DOI']
            tagsDict = dict(zip(tags, ref))
        except:
            continue

        ref = referenceOrderEditor(tagsDict, newNamesFormat, newformat)
        ref = ref_to_string(ref)
        f.write(ref)
        print(ref)

    f.close()



#workmode = 'test'
workmode = 'prod'

if workmode == 'test':
    testmode = 1
    if testmode == '1':
        print('Debug mode')
        URL = 'https://doi.org/10.1021/acs.chemmater.9b03963'
        tmpref = parser(URL)
        print(referenceOrderEditor(tmpref, newNamesFormat, newformat))
    else:
        startparser(sourcefile, newNamesFormat, newformat)


