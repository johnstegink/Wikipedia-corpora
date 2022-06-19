# Script to create a corpus based on wikipedia.
# run as: wikidatacorpus.py -s <subject> -o <outputdirectory>

import sys,argparse

import Sections
import functions
from Wikidata import Wikidata
from Sections import Sections
from Links import Links
import os

# Constants
wikidata_enpoint = "https://query.wikidata.org/sparql"
wikipedia_dumpdir = "../../WikipediaDump"

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


def save_article(wikidata, row, output):
    """
    Save the row (id, url). Retreive the text and the connections
    :param row:
    :param output: output directory
    :return:
    """

    lemma = wikidata.url_to_name(row[1])
    if not lemma is None:
        xml = wikidata.read_wikipedia_article(lemma)
        filename = os.path.join(output, f"{lemma}.xml")
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
            save_article(wikidata, row, output)


def step2( input_dir, output_dir):
    """
    Perform step2, splitting articles into sections
    :param input_dir:
    :param output_dir:
    :return:
    """
    files = functions.read_all_files_from_directory(input_dir, "xml")
    functions.create_directory_if_not_exists(output_dir)

    currentid = 1
    for file in files:
        contents = functions.read_file(file)
        name = os.path.splitext(os.path.basename(file))[0]

        sections = Sections( contents, currentid, output_dir)
        sections.create_sections()
        currentid += 1

def step3( input_dir, output_dir):
    """
    Creates a tsv file with links from one ID to another
    :param input_dir:
    :param linkfile:
    :return:
    """

    functions.create_directory_if_not_exists(output_dir)
    files = functions.read_all_files_from_directory(input_dir, "xml")

    links = Links( files)
    links.read_links()
    links.save_distance(output_dir)



# Main part of the script
if __name__ == '__main__':
    (subjects, output, language) = read_arguments()

    # Read all data from wikipedia
    # step1(subjects, language, os.path.join(output, "step1"))

    # Split the articles into sections
    # step2(os.path.join(output, "step1"), os.path.join(output, "step2"))

    # Create a link file based on the input
    step3(os.path.join(output, "step2"), os.path.join(output, "step3"))




