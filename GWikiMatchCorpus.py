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
number_of_threads = 8
wikipedia_dumpdir = "../../WikipediaDump"
gwikimatch_dir = "GWikiMatch"


def read_arguments():
    """
    Read arguments from the command line
    :return: (outputdirectory, language)
    """

    parser = argparse.ArgumentParser(description='Read articles from wikipedia based on the gWikiDataset.')
    parser.add_argument('-l', '--language', help='Language code, for example "nl" or "en"', required=True, default="en")
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = vars(parser.parse_args())

    return (args["output"], args["language"].lower())


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
        number_of_sections = sections.create_sections()
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



    # threads = []
    # chunk_size = math.ceil( len(files) / number_of_threads)
    # for thread_nr in range(0, number_of_threads):
    #     thread = threading.Thread(target=save_distance, args=( links, output_dir, treshold, thread_nr * chunk_size, (thread_nr + 1) * chunk_size - 1))
    #     threads.append(thread)
    #
    # for thread in threads:
    #     thread.start()
    #
    # for thread in threads:
    #     thread.join()




# Main part of the script
if __name__ == '__main__':
    (output, language) = read_arguments()

    wikimatch = GWikiMatch(dir=gwikimatch_dir, wikidata_endpoint=wikidata_enpoint, debug=False)
    articles = wikimatch.get_all_articles_with_url( language)

