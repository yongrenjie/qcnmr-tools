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

    #print(doi_dict)



# {Higashibayashi, Shuhei and Czechtizky, Werngard and Kobayashi, Yoshihisa and Kishi, Yoshito}

# 10.1002/anie.201708266


dict = {'indexed': {'date-parts': [[2019, 2, 18]], 'date-time': '2019-02-18T12:48:38Z', 'timestamp': 1550494118012},
        'reference-count': 53,
        'publisher': 'Wiley',
        'issue': '46',
        'license': [{'URL': 'http://doi.wiley.com/10.1002/tdm_license_1.1', 'start': {'date-parts': [[2017, 10, 11]], 'date-time': '2017-10-11T00:00:00Z', 'timestamp': 1507680000000}, 'delay-in-days': 0, 'content-version': 'tdm'}, {'URL': 'http://creativecommons.org/licenses/by-nc-nd/4.0/', 'start': {'date-parts': [[2017, 10, 11]], 'date-time': '2017-10-11T00:00:00Z', 'timestamp': 1507680000000}, 'delay-in-days': 0, 'content-version': 'vor'}], 'content-domain': {'domain': [], 'crossmark-restriction': False},
        'short-container-title': ['Angew. Chem. Int. Ed.'],
        'published-print': {'date-parts': [[2017, 11, 13]]},
        'DOI': '10.1002/anie.201708266',
        'type': 'journal-article',
        'created': {'date-parts': [[2017, 9, 14]], 'date-time': '2017-09-14T10:22:42Z', 'timestamp': 1505384562000},
        'page': '14763-14769',
        'source': 'Crossref',
        'is-referenced-by-count': 19,
        'title': ['Fully Automated Quantum-Chemistry-Based Computation of Spin-Spin-Coupled Nuclear Magnetic Resonance Spectra'],
        'prefix': '10.1002',
        'volume': '56',
        'author': [{'ORCID': 'http://orcid.org/0000-0002-5844-4371', 'authenticated-orcid': False, 'given': 'Stefan', 'family': 'Grimme', 'sequence': 'first', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'ORCID': 'http://orcid.org/0000-0003-3242-496X', 'authenticated-orcid': False, 'given': 'Christoph', 'family': 'Bannwarth', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'given': 'Sebastian', 'family': 'Dohm', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'ORCID': 'http://orcid.org/0000-0003-1659-8206', 'authenticated-orcid': False, 'given': 'Andreas', 'family': 'Hansen', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'given': 'Jana', 'family': 'Pisarek', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'given': 'Philipp', 'family': 'Pracht', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'given': 'Jakob', 'family': 'Seibert', 'sequence': 'additional', 'affiliation': [{'name': 'Mulliken Center for Theoretical Chemistry; Institut für Physikalische und Theoretische Chemie der Universität Bonn; Beringstrasse 4 53115 Bonn Germany'}]}, {'ORCID': 'http://orcid.org/0000-0003-4691-0547', 'authenticated-orcid': False, 'given': 'Frank', 'family': 'Neese', 'sequence': 'additional', 'affiliation': [{'name': 'Max Planck Institute for Chemical Energy Conversion; Stiftstrasse 32-34 45470 Mülheim an der Ruhr Germany'}]}], 'member': '311', 'published-online': {'date-parts': [[2017, 10, 11]]},
        'reference': [{'key': '10.1002/anie.201708266-BIB0001|anie201708266-cit-0001', 'author': 'Pople', 'year': '1959', 'volume-title': 'High-Resolution Nuclear Magnetic Resonance'}, {'key': '10.1002/anie.201708266-BIB0002|anie201708266-cit-0002', 'author': 'Günther', 'year': '2013', 'volume-title': 'NMR Spectroscopy-Basic Principles, Concepts and Applications in Chemistry'}, {'key': '10.1002/anie.201708266-BIB0003|anie201708266-cit-0003', 'author': 'Helgaker', 'volume': '99', 'first-page': '293', 'year': '1999', 'journal-title': 'Chem. Rev.', 'DOI': '10.1021/cr960017t', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0003.2|anie201708266-cit-0004', 'author': 'Helgaker', 'volume': '53', 'first-page': '249', 'year': '2008', 'journal-title': 'Prog. Nucl. Magn. Reson. Spectrosc.', 'DOI': '10.1016/j.pnmrs.2008.02.002', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0003.3|anie201708266-cit-0005', 'author': 'Mühl', 'volume': '1', 'first-page': '634', 'year': '2011', 'journal-title': 'WIREs Comput. Mol. Sci.', 'DOI': '10.1002/wcms.63', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0003.4|anie201708266-cit-0006', 'author': 'Lodewyk', 'volume': '112', 'first-page': '1839', 'year': '2012', 'journal-title': 'Chem. Rev.', 'DOI': '10.1021/cr200106v', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0004|anie201708266-cit-0007', 'author': 'Xin', 'volume': '82', 'first-page': '5135', 'year': '2017', 'journal-title': 'J. Org. Chem.', 'DOI': '10.1021/acs.joc.7b00321', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0004.2|anie201708266-cit-0008', 'author': 'Kutateladze', 'volume': '80', 'first-page': '5218', 'year': '2015', 'journal-title': 'J. Org. Chem.', 'DOI': '10.1021/acs.joc.5b00619', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0005|anie201708266-cit-0009', 'author': 'Bagno', 'volume': '7', 'first-page': '1652', 'year': '2001', 'journal-title': 'Chem. Eur. J.', 'DOI': '10.1002/1521-3765(20010417)7:8<1652::AID-CHEM16520>3.0.CO;2-V', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0006|anie201708266-cit-0010', 'author': 'Teale', 'volume': '138', 'first-page': '024111', 'year': '2013', 'journal-title': 'J. Chem. Phys.', 'DOI': '10.1063/1.4773016', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0007|anie201708266-cit-0011', 'author': 'Flaig', 'volume': '10', 'first-page': '572', 'year': '2014', 'journal-title': 'J. Chem. Theory Comput.', 'DOI': '10.1021/ct400780f', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0008|anie201708266-cit-0012', 'author': 'Benassi', 'volume': '38', 'first-page': '87', 'year': '2017', 'journal-title': 'J. Comput. Chem.', 'DOI': '10.1002/jcc.24521', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0009|anie201708266-cit-0013', 'author': 'Abraham', 'year': '2008', 'volume-title': 'Modelling 1H-NMR Spectra of Organic Compounds: Theory, Applications and NMR Prediction Software', 'DOI': '10.1002/9780470721803', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0010|anie201708266-cit-0014', 'author': 'Willoughby', 'volume': '9', 'first-page': '643', 'year': '2014', 'journal-title': 'Nat. Protoc.', 'DOI': '10.1038/nprot.2014.042', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0011|anie201708266-cit-0015', 'author': 'Castillo', 'volume': '209', 'first-page': '123', 'year': '2011', 'journal-title': 'J. Magn. Reson.', 'DOI': '10.1016/j.jmr.2010.12.008', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0012|anie201708266-cit-0016', 'author': 'Adamo', 'volume': '110', 'first-page': '6158', 'year': '1999', 'journal-title': 'J. Chem. Phys.', 'DOI': '10.1063/1.478522', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0012.2|anie201708266-cit-0017', 'author': 'Jensen', 'volume': '126', 'first-page': '371', 'year': '2010', 'journal-title': 'Theor. Chem. Acc.', 'DOI': '10.1007/s00214-009-0699-5', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0012.3|anie201708266-cit-0018', 'author': 'Jensen', 'volume': '4', 'first-page': '719', 'year': '2008', 'journal-title': 'J. Chem. Theory Comput.', 'DOI': '10.1021/ct800013z', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0012.4|anie201708266-cit-0019', 'author': 'Helgaker', 'volume': '81', 'first-page': '11496', 'year': '2016', 'journal-title': 'J. Org. Chem.', 'DOI': '10.1021/acs.joc.6b02157', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013|anie201708266-cit-0020', 'author': 'Kozuch', 'volume': '114', 'first-page': '20801', 'year': '2010', 'journal-title': 'J. Phys. Chem. C', 'DOI': '10.1021/jp1070852', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013.2|anie201708266-cit-0021', 'author': 'Grimme', 'volume': '143', 'first-page': '054107', 'year': '2015', 'journal-title': 'J. Chem. Phys.', 'DOI': '10.1063/1.4927476', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013.3|anie201708266-cit-0022', 'author': 'Klamt', 'first-page': '799', 'year': '1993', 'journal-title': 'J. Chem. Soc. Perkin Trans. 2', 'DOI': '10.1039/P29930000799', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013.4|anie201708266-cit-0023', 'author': 'Eckert', 'volume': '48', 'first-page': '369', 'year': '2002', 'journal-title': 'AiChE J.', 'DOI': '10.1002/aic.690480220', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013.5|anie201708266-cit-0024', 'author': 'Sinnecker', 'volume': '110', 'first-page': '2235', 'year': '2006', 'journal-title': 'J. Phys. Chem. A', 'DOI': '10.1021/jp056016z', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0013.6|anie201708266-cit-0025', 'author': 'Weigend', 'volume': '7', 'first-page': '3297', 'year': '2005', 'journal-title': 'Phys. Chem. Chem. Phys.', 'DOI': '10.1039/b508541a', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0014|anie201708266-cit-0026', 'unstructured': 'ORCA-An Ab Initio, DFT and Semiempirical electronic structure package Ver. 4.0.1 2017'}, {'key': '10.1002/anie.201708266-BIB0014.2|anie201708266-cit-0027', 'author': 'Neese', 'volume': '2', 'first-page': '73', 'year': '2012', 'journal-title': 'WIREs Comput. Mol. Sci.', 'DOI': '10.1002/wcms.81', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0015|anie201708266-cit-0028', 'unstructured': 'TURBOMOLE\u20057.2 2017 http://www.turbomole.com'}, {'key': '10.1002/anie.201708266-BIB0016|anie201708266-cit-0029', 'unstructured': 'http://goldbook.iupac.org/html/C/C01262.html http://goldbook.iupac.org/html/R/R05407.html'}, {'key': '10.1002/anie.201708266-BIB0017|anie201708266-cit-0030', 'author': 'Grimme', 'volume': '13', 'first-page': '1989', 'year': '2017', 'journal-title': 'J. Chem. Theory Comput.', 'DOI': '10.1021/acs.jctc.7b00118', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0018|anie201708266-cit-0031', 'unstructured': ''}, {'key': '10.1002/anie.201708266-BIB0019|anie201708266-cit-0032', 'author': 'Ásgeirsson', 'volume': '8', 'first-page': '4879', 'year': '2017', 'journal-title': 'Chem. Sci.', 'DOI': '10.1039/C7SC00601B', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0019.2|anie201708266-cit-0033', 'unstructured': 'J. Comput. Chem 2017 https://doi.org/10.1002/jcc.24922', 'DOI': '10.1002/jcc.24922', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0019.3|anie201708266-cit-0034', 'unstructured': 'Inorg. Chem 2017 https://doi.org/10.1021/acs.inorgchem.7b01950', 'DOI': '10.1021/acs.inorgchem.7b01950', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0019.4|anie201708266-cit-0035', 'author': 'Ye', 'volume': '53', 'first-page': '633', 'year': '2017', 'journal-title': 'Chem. Commun.', 'DOI': '10.1039/C6CC07071J', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020|anie201708266-cit-0036', 'author': 'Kolossváry', 'volume': '118', 'first-page': '5011', 'year': '1996', 'journal-title': 'J. Am. Chem. Soc.', 'DOI': '10.1021/ja952478m', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020.2|anie201708266-cit-0037', 'author': 'Kamachi', 'volume': '56', 'first-page': '347', 'year': '2016', 'journal-title': 'J. Chem. Inf. Model.', 'DOI': '10.1021/acs.jcim.5b00671', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020.3|anie201708266-cit-0038', 'author': 'Tsujishita', 'volume': '11', 'first-page': '305', 'year': '1997', 'journal-title': 'J. Comput.-Aided Mol. Des.', 'DOI': '10.1023/A:1007964913898', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020.4|anie201708266-cit-0039', 'author': 'Shim', 'volume': '2', 'first-page': '356', 'year': '2011', 'journal-title': 'MedChemComm', 'DOI': '10.1039/c1md00044f', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020.5|anie201708266-cit-0040', 'author': 'Jones', 'volume': '9', 'first-page': '532', 'year': '1995', 'journal-title': 'J. Comput.-Aided Mol. Des.', 'DOI': '10.1007/BF00124324', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0020.6|anie201708266-cit-0041', 'author': 'Vainio', 'volume': '47', 'first-page': '2462', 'year': '2007', 'journal-title': 'J. Chem. Inf. Model.', 'DOI': '10.1021/ci6005646', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0021|anie201708266-cit-0042', 'author': 'Pescitelli', 'volume': '40', 'first-page': '4603', 'year': '2011', 'journal-title': 'Chem. Soc. Rev.', 'DOI': '10.1039/c1cs15036g', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0022|anie201708266-cit-0043', 'author': 'Kaupp', 'first-page': '91', 'year': '2009', 'volume-title': 'Computational Inorganic and Bioinorganic Chemistry (in Encyclopedia of Inorganic Chemistry)'}, {'key': '10.1002/anie.201708266-BIB0023|anie201708266-cit-0044', 'author': 'Kwan', 'volume': '11', 'first-page': '5083', 'year': '2015', 'journal-title': 'J. Chem. Theory Comput.', 'DOI': '10.1021/acs.jctc.5b00856', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0024|anie201708266-cit-0045', 'author': 'Dracinsky', 'volume': '9', 'first-page': '3806', 'year': '2013', 'journal-title': 'J. Chem. Theory Comput.', 'DOI': '10.1021/ct400282h', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0025|anie201708266-cit-0046', 'unstructured': 'http://sdbs.db.aist.go.jp http://www.bmrb.wisc.edu/metabolomics'}, {'key': '10.1002/anie.201708266-BIB0026|anie201708266-cit-0047', 'author': 'Shaver', 'volume': '3', 'first-page': '1823', 'year': '1984', 'journal-title': 'Organometallics', 'DOI': '10.1021/om00090a008', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0027|anie201708266-cit-0048', 'author': 'Gansäuer', 'volume': '27', 'first-page': '5699', 'year': '2008', 'journal-title': 'Organometallics', 'DOI': '10.1021/om800700c', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0028|anie201708266-cit-0049', 'author': 'Ruud', 'volume': '123', 'first-page': '4826', 'year': '2001', 'journal-title': 'J. Am. Chem. Soc.', 'DOI': '10.1021/ja004160m', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0029|anie201708266-cit-0050', 'author': 'Pung', 'volume': '121', 'first-page': '6823', 'year': '2017', 'journal-title': 'J. Phys. Chem. A', 'DOI': '10.1021/acs.jpca.7b05197', 'doi-asserted-by': 'crossref'}, {'key': '10.1002/anie.201708266-BIB0030|anie201708266-cit-0051', 'unstructured': ''}, {'key': '10.1002/anie.201708266-BIB0030a|anie201708266-cit-0052', 'unstructured': 'http://www.acdlabs.com'}, {'key': '10.1002/anie.201708266-BIB0030b|anie201708266-cit-0053', 'unstructured': 'http://www.nmrdb.org'}], 'container-title': ['Angewandte Chemie International Edition'], 'original-title': [], 'language': 'en', 'link': [{'URL': 'https://api.wiley.com/onlinelibrary/tdm/v1/articles/10.1002%2Fanie.201708266', 'content-type': 'application/pdf', 'content-version': 'vor', 'intended-application': 'text-mining'}, {'URL': 'https://onlinelibrary.wiley.com/doi/full/10.1002/anie.201708266', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'similarity-checking'}], 'deposited': {'date-parts': [[2018, 8, 6]], 'date-time': '2018-08-06T04:27:05Z', 'timestamp': 1533529625000}, 'score': 1.0, 'subtitle': [], 'short-title': [], 'issued': {'date-parts': [[2017, 10, 11]]}, 'references-count': 53, 'journal-issue': {'published-print': {'date-parts': [[2017, 11, 13]]}, 'issue': '46'}, 'URL': 'http://dx.doi.org/10.1002/anie.201708266', 'archive': ['Portico'], 'relation': {'cites': []}, 'ISSN': ['1433-7851'], 'issn-type': [{'value': '1433-7851', 'type': 'print'}]}



{'indexed': {'date-parts': [[2019, 4, 3]], 'date-time': '2019-04-03T16:14:13Z', 'timestamp': 1554308053698}, 'reference-count': 68, 'publisher': 'American Chemical Society (ACS)', 'funder': [{'DOI': '10.13039/100011110', 'name': 'UCB', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100004319', 'name': 'Pfizer', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100008897', 'name': 'Janssen Pharmaceuticals', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/501100000266', 'name': 'Engineering and Physical Sciences Research Council', 'doi-asserted-by': 'publisher', 'award': ['EP/M019195/1']}, {'DOI': '10.13039/100011022', 'name': 'Vertex Pharmaceuticals', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100008373', 'name': 'Takeda Pharmaceutical Company', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100004330', 'name': 'GlaxoSmithKline', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/501100000769', 'name': 'University of Oxford', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100004325', 'name': 'AstraZeneca', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/501100010761', 'name': 'Syngenta International', 'doi-asserted-by': 'crossref', 'award': []}, {'DOI': '10.13039/100004336', 'name': 'Novartis', 'doi-asserted-by': 'publisher', 'award': []}, {'DOI': '10.13039/100010418', 'name': 'Defence Science and Technology Laboratory', 'doi-asserted-by': 'publisher', 'award': []}, {'name': 'Evotec', 'award': []}], 'content-domain': {'domain': [], 'crossmark-restriction': False}, 'short-container-title': ['Org. Lett.'], 'DOI': '10.1021/acs.orglett.9b00971', 'type': 'journal-article', 'created': {'date-parts': [[2019, 4, 3]], 'date-time': '2019-04-03T15:33:27Z', 'timestamp': 1554305607000}, 'source': 'Crossref', 'is-referenced-by-count': 0, 'title': ['A General Copper-Catalyzed Synthesis of Ynamides from 1,2-Dichloroenamides'], 'prefix': '10.1021', 'author': [{'given': 'Steven J.', 'family': 'Mansfield', 'sequence': 'first', 'affiliation': [{'name': 'Chemistry Research Laboratory, 12 Mansfield Road, Oxford, OX1 3TA, U.K.'}]}, {'given': 'Russell C.', 'family': 'Smith', 'sequence': 'additional', 'affiliation': [{'name': 'Janssen PRD, 3210 Merryfield Row, San Diego, California 92121, United States'}]}, {'given': 'Jonathan R. J.', 'family': 'Yong', 'sequence': 'additional', 'affiliation': [{'name': 'Chemistry Research Laboratory, 12 Mansfield Road, Oxford, OX1 3TA, U.K.'}]}, {'given': 'Olivia L.', 'family': 'Garry', 'sequence': 'additional', 'affiliation': [{'name': 'Chemistry Research Laboratory, 12 Mansfield Road, Oxford, OX1 3TA, U.K.'}]}, {'ORCID': 'http://orcid.org/0000-0002-4149-0494', 'authenticated-orcid': True, 'given': 'Edward A.', 'family': 'Anderson', 'sequence': 'additional', 'affiliation': [{'name': 'Chemistry Research Laboratory, 12 Mansfield Road, Oxford, OX1 3TA, U.K.'}]}], 'member': '316', 'published-online': {'date-parts': [[2019, 4, 3]]}, 'container-title': ['Organic Letters'], 'original-title': [], 'language': 'en', 'link': [{'URL': 'http://pubs.acs.org/doi/pdf/10.1021/acs.orglett.9b00971', 'content-type': 'unspecified', 'content-version': 'vor', 'intended-application': 'similarity-checking'}], 'deposited': {'date-parts': [[2019, 4, 3]], 'date-time': '2019-04-03T15:40:20Z', 'timestamp': 1554306020000}, 'score': 1.0, 'subtitle': [], 'short-title': [], 'issued': {'date-parts': [[2019, 4, 3]]}, 'references-count': 68, 'alternative-id': ['10.1021/acs.orglett.9b00971'], 'URL': 'http://dx.doi.org/10.1021/acs.orglett.9b00971', 'relation': {}, 'ISSN': ['1523-7060', '1523-7052'], 'issn-type': [{'value': '1523-7060', 'type': 'print'}, {'value': '1523-7052', 'type': 'electronic'}], 'subject': ['Physical and Theoretical Chemistry', 'Organic Chemistry', 'Biochemistry'], 'article-number': 'acs.orglett.9b00971'}
