# Script to create a corpus based on wikipedia.
# run as: wikidatacorpus.py -s <subject> -o <outputdirectory>

import sys,argparse
from Wikidata import Wikidata
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



# Main part of the script
if __name__ == '__main__':
    (subjects, output, language) = read_arguments()

    wikidata = Wikidata(wikidata_endpoint=wikidata_enpoint, subjects=subjects, dump_dir=wikipedia_dumpdir, language=language, debug=False)
    urls = wikidata.read_all_items()
    if output == "" or output is None:
        print( len(urls))
    else:
        for url in urls:
            lemma = wikidata.url_to_name( url)
            xml = wikidata.read_wikipedia_article( lemma)
            filename = os.path.join( output, f"{lemma}.xml")

            file = open(filename, mode="w", encoding="utf-8")
            file.write(xml)
            file.close()




