#!/usr/bin/env python3

# feed this a DOI and it will generate a BibLaTeX entry and copy it to your clipboard
# pip3 install crossrefapi
# pip3 install pyperclip

from crossref.restful import Works, Etiquette
import sys
import pyperclip
my_etiquette = Etiquette('DOI to BibLaTeX', '0.1', 'https://github.com/yongrenjie/qcnmr-tools', 'yongrenjie@gmail.com')


def parse_given_names(given_names):
    # converts "Jonathan R. J." to "J. R. J."
    parsed_names = ""
    for name in given_names:
        parsed_names = parsed_names + name[0] + ". "
    return parsed_names[:-1]


if __name__ == '__main__':
    works = Works(etiquette=my_etiquette)

    if len(sys.argv) == 2:
        doi = sys.argv[1]
    else:
        doi = input("Please enter DOI: ")

    doi_dict = works.doi(doi)

    short_journal_name = doi_dict["short-container-title"][0]
    article_title = doi_dict["title"][0]

    try:
        pages = doi_dict["page"]
    except:
        pages = ""

    # just change this to LaTeX en dash
    pages = pages.replace("-", "--")

    authors = doi_dict["author"]

    try:
        year = doi_dict['published-print']['date-parts'][0][0]
    except:
        year = doi_dict['published-online']['date-parts'][0][0]

    try:
        volume = doi_dict['volume']
    except:
        volume = ""
    try:
        issue = doi_dict['issue']
    except:
        issue = ""

    # parse author names and produce BibLaTeX string
    parsed_author_names = ""
    for author in authors:
        family_name = author['family']
        given_names = author['given']
        parsed_author_names = parsed_author_names + family_name + ", " + given_names + " and "
    parsed_author_names = parsed_author_names[:-5]

    reference_name = parsed_author_names.split(",")[0] + str(year)

    biblatex_citation = ""
    biblatex_citation = biblatex_citation + "@article{{{},\n".format(reference_name)
    biblatex_citation = biblatex_citation + "doi = {{{}}},\n".format(doi)
    biblatex_citation = biblatex_citation + "author = {{{}}},\n".format(parsed_author_names)
    biblatex_citation = biblatex_citation + "journal = {{{}}},\n".format(short_journal_name)
    biblatex_citation = biblatex_citation + "title = {{{{{}}}}},\n".format(article_title)
    biblatex_citation = biblatex_citation + "year = {{{}}},\n".format(year)
    if volume:
        biblatex_citation = biblatex_citation + "volume = {{{}}},\n".format(volume)
    if issue:
        biblatex_citation = biblatex_citation + "issue = {{{}}},\n".format(issue)
    if pages:
        biblatex_citation = biblatex_citation + "pages = {{{}}},\n".format(pages)
    biblatex_citation = biblatex_citation + "}"

    print()
    print(biblatex_citation)
    print()
    pyperclip.copy(biblatex_citation)
    print("Reference copied to clipboard.")
    print()
