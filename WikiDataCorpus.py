# Script to create a corpus based on wikipedia.
# run as: wikidatacorpus.py -s <subject> -o <outputdirectory>
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
gwikimatch_dir = "GWikiMatch"


def read_arguments():
    """
    Read arguments from the command line
    :return: (subject, outputdirectory, language)
    """

    parser = argparse.ArgumentParser(description='Read articles from wikipedia based on WikiData option.')
    parser.add_argument('-s', '--subjects', help='Main wikidata subjects', required=True)
    parser.add_argument('-l', '--language', help='Language code, for example "nl" or "en"', required=True, default="en")
    parser.add_argument('-o', '--output', help='Output directory, when no output is given the count will be printed', required=False)
    args = vars(parser.parse_args())


    subjects = args["subjects"].split(",")
    message = Wikidata.check_property(subjects)
    if message != "":
        print( message)
        exit( 3)

    if not "output" in args:
        output = ""
    else:
        output = args["output"]

    return (subjects,output, args["language"].lower())


def save_article(wikidata, wikidata_id, name, output):
    """
    Save the row (id, url). Retrieve the text and the connections
    :param row:
    :param output: output directory
    :return:
    """

    lemma = wikidata.url_to_name(name)
    id = wikidata_id.replace("wd:", "")
    if not lemma is None:
        xml = wikidata.read_wikipedia_article(id, lemma)
        filename = os.path.join(output, id + ".xml")
        if not xml is None:
            functions.write_file(filename, str(xml))


def step1(subjects, language, output):
    """
    Perform step1, extract data from Wikidata into xml files
    :param subjects:
    :param language:
    :param output:
    :return:
    """
    wikidata = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=subjects, dump_dir=wikipedia_dumpdir,
                        language=language, debug=False)
    rows = wikidata.read_all_items()
    if output == "" or output is None:
        print(len(rows))
    else:
        functions.create_directory_if_not_exists(output)
        for row in rows:
            save_article(wikidata, wikidata_id=row[0], name=row[1], output=output)


def step2( input_dir, output_dir):
    """
    Perform step2, splitting articles into sections, and returns statistics in a tuple
    :param input_dir:
    :param output_dir:
    :return: (articles, with_sections, with_sections, without_sections, total_sections)
    """
    files = functions.read_all_files_from_directory(input_dir, "xml")
    functions.create_directory_if_not_exists(output_dir)

    total_sections = 0
    total_articles_with_sections = 0
    total_articles_without_sections = 0

    counter = 1
    for file in files:
        contents = functions.read_file(file)
        name = os.path.splitext(os.path.basename(file))[0]

        sections = Sections( contents, name, output_dir)
        number_of_sections = sections.create_sections(with_keys=True, links=[])
        total_sections += number_of_sections
        if( number_of_sections > 0):
            total_articles_with_sections += 1
        else:
            total_articles_without_sections += 1

        counter += 1

    return( counter - 1, total_articles_with_sections, total_articles_without_sections, total_sections)


def save_distance(links, output_dir, treshold, start_index, end_index):
    links.save_distance(output_dir, treshold, start_index, end_index)


def step3( input_dir, output_dir, treshold):
    """
    Creates a tsv file with links from one ID to another
    :param input_dir:
    :param linkfile:
    :return:
    """

    functions.create_directory_if_not_exists(output_dir)
    files = functions.read_all_files_from_directory(input_dir, "xml")

    links = Links( files)
    name_id = links.read_name_id()
    links.read_links( name_id)
    links.save_distance(output_dir, treshold, 0, len(files))




# Main part of the script
if __name__ == '__main__':
    (subjects, output, language) = read_arguments()

    wikimatch = GWikiMatch(dir=gwikimatch_dir, wikidata_endpoint=wikidata_enpoint, debug=False)

    # Read all data from wikipedia
    step1(subjects, language, os.path.join(output, "step1"))

    # Split the articles into sections
    (articles, with_sections, without_sections, total_sections) = step2(os.path.join(output, "step1"), os.path.join(output, "step2"))

    # Write the statistics
    stats_file = os.path.join(output, "stats.txt")
    functions.write_file(stats_file, f"Number of articles               : {articles}" +
                                     f"Number articles with sections    : {with_sections}" +
                                     f"Total number of sections         : {total_sections}" +
                                     f"Number articles without sections : {without_sections}" +
                                     f"Percentage articles with sections: {(articles / with_sections):0.2f}"
                         );


    # Create a link file based on the input
    step3(os.path.join(output, "step2"), os.path.join(output, "step3"), 0.3)

    ids = [ os.path.basename( file).replace(".xml", "") for file in functions.read_all_files_from_directory( os.path.join(output, "step1"), "xml")]
    wikimatch.create_filtered_file( os.path.join(output, "gwikimatch.tsv"), set(ids))

