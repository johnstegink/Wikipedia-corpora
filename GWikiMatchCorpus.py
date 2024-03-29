# Script to create a corpus based on gwikimatch
# run as: gwikimatch.py -l <language> -o <outputdirectory>
import math
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


def read_arguments():
    """
    Read arguments from the command line
    :return: (outputdirectory, language)
    """

    parser = argparse.ArgumentParser(description='Read articles from wikipedia based on the gWikiDataset.')
    parser.add_argument('-l', '--language', help='Language code, for example "nl" or "en"', required=True, default="en")
    parser.add_argument('-i', '--input', help='Input directory (relative to this script)', required=True)
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = vars(parser.parse_args())

    return (args["input"], args["output"], args["language"].lower())



def save_article(wikidata, wikidata_id, name, links, output):
    """
    Save the row (id, url) in an xml file
    :param row:
    :param output: output directory
    :return:
    """

    lemma = wikidata.url_to_name(name)
    id = wikidata_id.replace("wd:", "")
    if not lemma is None:
        xml = wikidata.read_wikipedia_article(id, lemma)
        if not xml is None:
            sections = Sections( contents=xml)
            sections.create_sections(with_keys=False, links=links, id=wikidata_id, output_dir=output)


# Main part of the script
if __name__ == '__main__':
    (input, output, language) = read_arguments()

    wikimatch = GWikiMatch(dir=input, wikidata_endpoint=wikidata_enpoint, debug=False)
    articles = wikimatch.get_all_articles_with_url( language)

    wikidata = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=[], dump_dir=wikipedia_dumpdir,
                        language=language, debug=False)

    functions.create_directory_if_not_exists(output)
    for article in articles:
        links = wikimatch.get_links_of_article( id=article[0])
        save_article(wikidata, wikidata_id=article[0], name=article[1], output=output, links=links)

    functions.write_corpus_info(output, "GWikiMatch " + language.upper(), "en")

    functions.write_article_pairs(output, wikimatch.info)
