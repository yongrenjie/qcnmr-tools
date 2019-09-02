#!/usr/bin/env python3

# feed this a DOI and it will generate a BibLaTeX entry and copy it to your clipboard
# pip3 install crossrefapi
# pip3 install pyperclip

from crossref.restful import Works, Etiquette
import sys
import pyperclip
my_etiquette = Etiquette('DOI to BibLaTeX',
                         '1.1',
                         'https://github.com/yongrenjie/qcnmr-tools/blob/master/doi2biblatex.py',
                         'yongrenjie@gmail.com')


# Dictionary containing correct (as listed in CASSI) abbreviations of some journals.
journal_abbreviations_dict = {
    "Proceedings of the National Academy of Sciences": "Proc. Acad. Natl. Sci. U. S. A.",
    "The Journal of Chemical Physics": "J. Chem. Phys.",
    "Journal of Magnetic Resonance": "J. Magn. Reson.",
    "Progress in Nuclear Magnetic Resonance Spectroscopy": "Prog. Nucl. Magn. Reson. Spectrosc.",
}


def parse_given_names(given_names):
    # converts "Jonathan R. J." to "J. R. J."
    parsed_names = ""
    for name in given_names:
        parsed_names = parsed_names + name[0] + ". "
    return parsed_names[:-1]


def remove_spaces(names):
    # converts "del Potro" to "delPotro"
    names_without_spaces = ""
    for name in names.split():
        names_without_spaces = names_without_spaces + name
    return names_without_spaces


if __name__ == '__main__':
    works = Works(etiquette=my_etiquette)

    clip = False
    if len(sys.argv) == 2:
        doi = sys.argv[1]
    elif len(sys.argv) == 3:
        # Checks if "-c" is one of the command-line options
        # If so, sets doi to the other one and enables clipboard; if not, sets doi to the longer option (useful for typos)
        if sys.argv[1] == "-c":
            doi = sys.argv[2]
            clip = True
        elif sys.argv[2] == "-c":
            doi = sys.argv[1]
            clip = True
        else:
            doi = sys.argv[1] if len(sys.argv[1]) >= len(sys.argv[2]) else sys.argv[2]
    else:
        sys.exit("Please specify a valid DOI. You can use the optional -c argument to copy the reference to the clipboard.")


    doi_dict = works.doi(doi)

    short_journal_name = doi_dict["short-container-title"][0]
    # replace the abbreviation if it's wrong
    if short_journal_name in journal_abbreviations_dict:
        short_journal_name = journal_abbreviations_dict[short_journal_name]

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

    reference_name = remove_spaces(parsed_author_names.split(",")[0]) + str(year)

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

    print(biblatex_citation)
    print()

    if clip:
        pyperclip.copy(biblatex_citation)
        print("Reference copied to clipboard.")
        print()
