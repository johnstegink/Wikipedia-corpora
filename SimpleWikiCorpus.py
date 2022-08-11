# Script to create a corpus based a selection from the simple wikipedia
# Combined with one of the normal wikipedia
import math
import random
import sys,argparse
import threading

import Sections
import functions
from Wikidata import Wikidata
from Sections import Sections
from GWikiMatch import GWikiMatch
from Links import Links
import os

# Constants
wikidata_enpoint = "https://query.wikidata.org/sparql"
wikipedia_dumpdir = "../../WikipediaDump"
number_of_random_articles = 1000
number_of_same_articles = 46

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
        if len( written) < count:
            id = f"{id_prefix}_{i + 1}"  # Dummy id

            xml = wikidata.read_wikipedia_article(id, lemmata[i])
            if not xml is None and not (wikidata.language == "simple"  and  "#redirect" in xml.lower()):
                sections = Sections( contents=xml)
                sections.create_sections(with_keys=False, links=[], id=id, output_dir=output)
                written.append( lemmata[i])

    functions.write_corpus_info(output, "Random " + wikidata.language.upper(), "en")
    return written


# Main part of the script
if __name__ == '__main__':
    (simple, english) = read_arguments()

    functions.create_directory_if_not_exists(simple)
    functions.create_directory_if_not_exists(english)

    simplewiki = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=[], dump_dir=wikipedia_dumpdir,
                        language="simple", debug=False)
    enwiki = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=[], dump_dir=wikipedia_dumpdir,
                        language="en", debug=False)

    # 46 Random articles starting with a
    a_articles = simplewiki.get_random_articles( exceptions=[], count=3 * number_of_random_articles, only_starting_with_a=True)

    # 1000 different articles
    random_simple = simplewiki.get_random_articles( exceptions=a_articles, count=(3 * number_of_random_articles), only_starting_with_a=False)
    a_articles = save_articles(simplewiki, a_articles, number_of_same_articles, "a", simple)
    save_articles(simplewiki, random_simple, number_of_random_articles, "r", simple)

    # 1000 english articles
    random_en = enwiki.get_random_articles( exceptions=a_articles, count=(3 * number_of_random_articles), only_starting_with_a=False)
    save_articles(enwiki, a_articles, number_of_random_articles, "a", english)
    save_articles(enwiki, a_articles, number_of_random_articles, "r", english)

