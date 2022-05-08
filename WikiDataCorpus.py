# Script to create a corpus based on wikipedia.
# run as: wikidatacorpus.py -s <subject> -o <outputdirectory>

import sys,argparse
from Wikidata import Wikidata

# Constants
wikidata_enpoint = "https://query.wikidata.org/sparql"

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



# Main part of the script
if __name__ == '__main__':
    (subjects, output, language) = read_arguments()

    wikidata = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=subjects, language=language, debug=False)
    urls = wikidata.read_all_items()
    if output == "" or output is None:
        print( len(urls))


