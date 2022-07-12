# Script to create a corpus based on gwikimatch
# run as: gwikimatch.py -l <language> -o <outputdirectory>
import math
import sys,argparse
import threading

from S2ORC import S2ORC
import functions
import os

# Constants


def read_arguments():
    """
    Read arguments from the command line
    :return: (metadata_directory, pdf_parses_directory, outputdirectory, subject)
    """

    parser = argparse.ArgumentParser(description='Read articles from wikipedia based on the gWikiDataset.')
    parser.add_argument('-s', '--subject', help='Subject, for example "Computer Science"', required=True, default="en")
    parser.add_argument('-p', '--pdfparses', help='Directory with pdf_parses', required=True)
    parser.add_argument('-m', '--metadata', help='Directory with meta_data', required=True)
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = vars(parser.parse_args())

    return (args["metadata"], args["pdfparses"], args["output"], args["subject"].lower())

# Main part of the script
if __name__ == '__main__':
    (metadata, pdf_parses, output, subject) = read_arguments()

    functions.create_directory_if_not_exists(os.path.join(output, subject))

    s2ORC = S2ORC(metadata=os.path.join(metadata, subject), pdf_parses=os.path.join(pdf_parses, subject))
    s2ORC.convert_to_xml( output_dir=os.path.join(output, subject))



