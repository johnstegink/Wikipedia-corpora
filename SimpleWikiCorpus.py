# Script to create a corpus based a selection from the simple wikipedia
# Combined with one of the normal wikipedia
import math
import random
import re
import sys,argparse
from lxml import etree as ET


import Sections
import functions
from Wikidata import Wikidata
from Sections import Sections
import os
import html
from urllib import parse

# Constants
wikidata_enpoint = "https://query.wikidata.org/sparql"
wikipedia_dumpdir = "../../WikipediaDump"
number_of_random_articles = 1000
number_of_same_articles = 46
minimumxmlsize = 255


def read_arguments():
    """
    Read arguments from the command line
    :return: (outputdirectory, language)
    """

    parser = argparse.ArgumentParser(description='Read articles pairs from the simple wikipedia and the english wikipedia.')
    parser.add_argument('-s', '--simple', help='Output directory of the normal wikipedia', required=True)
    parser.add_argument('-e', '--english', help='Output directory of the simple wikipedia', required=True)
    args = vars(parser.parse_args())

    return (args["simple"], args["english"])


def length_of_text_in_xml( xml):
    """
    Determines the length of the text in the Xml (without the Xml elements)
    :param xml:
    :return:
    """
    tree = ET.fromstring( xml)
    text = ET.tostring(tree, encoding='utf-8', method='text')
    return len( text)


def save_articles(wikidata, lemmata, count, id_prefix, output):
    """
    Save the articles
    :param wikidata: the wikidata instance
    :param lemmata: the list of lemmata
    :param output: output directory
    :param count: the number of articles to write
    :param prefox: prefix for the id
    :return: the names of the written articles
    """

    written = []

    for i in range(0, len(lemmata)):
        if len( written)  < count:
            id = f"{id_prefix}_{i + 1}"  # Dummy id

            xml = wikidata.read_wikipedia_article(id, lemmata[i])
            if not xml is None:
                sections = Sections( contents=xml)
                (xml, nrofsections) = sections.create_sections_xml(with_keys=False, links=[], id=id)

                # Skip the short lemmata
                if length_of_text_in_xml(xml) >= minimumxmlsize:
                    filename = os.path.join(output, f"{id}.xml")
                    functions.write_file(filename, xml)

                    written.append( lemmata[i])

    functions.write_corpus_info(output, "Random " + wikidata.language.upper(), "en")
    return written


def create_link( lemma, language):
    name = parse.quote(lemma.replace(" ", "_"))
    url = f"https://{language}.wikipedia.org/wiki/{name}"
    return f"<a href='{html.escape(url)}' target='_blank'>{html.escape(lemma)}</a>"

def create_html( lemmata, output):
    with open(output, "w", encoding="utf-8-sig") as f:
        f.write("<html><head><meta charset='UTF-8'></head><body><table>\n")
        f.write("<tr><th>Simple</th><th>English</th></tr>\n")
        for lemma in lemmata:
            f.write("<tr>\n")
            f.write("<td>" + create_link( lemma, "simple") + "</td>\n")
            f.write("<td>" + create_link( lemma, "en") + "</td>\n")
            f.write("</tr>\n")
        f.write("</table></body></html>")

def remove_all_files( dir):
    import glob
    files = glob.glob(f"{dir}/*")
    for f in files:
        os.remove(f)

# Main part of the script
if __name__ == '__main__':
    (simple, english) = read_arguments()

    functions.create_directory_if_not_exists(simple)
    functions.create_directory_if_not_exists(english)
    remove_all_files( simple)
    remove_all_files( english)

    simplewiki = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=[], dump_dir=wikipedia_dumpdir,
                        language="simple", debug=False)

    enwiki = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=[], dump_dir=wikipedia_dumpdir,
                        language="en", debug=False)

    # 46 Random articles starting with a
    a_articles = \
        ['Arrondissements of the Haute-Marne department', 'Alexander Litvinenko', 'Arnol Kox', 'Ali Boumnijel',
         'Atze Schröder', 'Allan Hunter (footballer)', 'Arab Winter', 'Aubessagne', 'Anthony Perkins', 'Abusir Papyri',
         'Ammonium chloride', 'A∴A∴', 'Ayaan Hirsi Ali', 'Avery–MacLeod–McCarty experiment', 'Arsenic trichloride',
         'Antimony triiodide', 'Alaska Airlines', 'Aldo Duscher', 'Antimony tribromide',
         "Alabama's 1st congressional district", 'Amazilia hummingbird', 'A. B. Raj', 'Angelos Charisteas',
         'Abbas Vaez-Tabasi', 'Allele', 'Appanage', 'Anne Nicol Gaylor', 'Antoine Lavoisier',
         'American Health Care Act of 2017', 'Ace Bailey', 'Axel Heiberg Island', 'Antoine Demoitié',
         'Armin van Buuren', 'Aqua Timez', 'Audio feedback', 'Anggun', 'Alliance for a Green Revolution in Africa',
         'AFC Cup', 'Aubignosc', 'Alex Morgan', 'Al-Shams (East Pakistan)', 'Acrolith', 'Alcindo Sartori',
         'Azerbaijani wine', 'Agen', 'Apollo Quiboloy']

    # a_articles = simplewiki.get_random_articles( exceptions=[], count=10 * number_of_same_articles, only_starting_with_a=True)
    # a_articles = save_articles(enwiki, a_articles, number_of_same_articles * 10, "a", english)
    # a_articles = save_articles(simplewiki, a_articles, number_of_same_articles * 10 , "a", simple)
    # a_46 = a_articles[0:46]

    create_html( a_articles, os.path.join( simple, "..", "a.html"))


    # 1000 random articles
    random_simple = simplewiki.get_random_articles( exceptions=a_articles, count=(10 * number_of_random_articles), only_starting_with_a=False)
    save_articles(simplewiki, a_articles, number_of_same_articles, "a", simple)
    simple_articles = save_articles(simplewiki, random_simple, number_of_random_articles, "r", simple)

    # 1000 english articles, exclude the lemmata used for the a_articles an the simple articles
    random_en = enwiki.get_random_articles( exceptions=(a_articles + simple_articles), count=(10 * number_of_random_articles), only_starting_with_a=False)
    save_articles(enwiki, a_articles, number_of_same_articles, "a", english)
    save_articles(enwiki, random_en, number_of_random_articles, "r", english)

