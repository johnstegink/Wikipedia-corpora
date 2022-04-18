# Script to create a corpus based on wikipedia.
# run as: wikidatacorpus.py -s <subject> -o <outputdirectory>

import sys,getopt
import Ontology

# Constants
wikidata_enpoint = "https://query.wikidata.org"

def read_arguments():
    """
    Read arguments from the command line
    :return: (subject, outputdirectory)
    """
    subject = ''
    output = ''

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"s:o:", ["subject=","output="])
    except getopt.GetoptError:
        print("wikidatacorpus.py -s <subject> -o <outputdirectory>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--subject"):
            subject = arg
        elif opt in ("-o", "--output"):
            output = arg

    # Check the subject
    message = Ontology.check_subject( subject)
    if message != "":
        print( message)
        exit( 3)

    return (subject,output)



# Main part of the script
if __name__ == '__main__':
    (subject, output) = read_arguments()

    wikidata = Ontology(wikidata_enpoint, subject)



