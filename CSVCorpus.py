# Script to create a corpus based on CSV files.
# run as: csvcorpus.py -f file -o <outputdirectory>
import sys,argparse

import functions
import os
import csv

# Global variables

texts = {}
links = {}
id_counter = 0


def read_arguments():
    """
    Read arguments from the command line
    :return: (file, outputdirectory)
    """

    parser = argparse.ArgumentParser(description='Read articles from wikipedia based on WikiData option.')
    parser.add_argument('-f', '--file', help='Path to the CSV file', required=True)
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = vars(parser.parse_args())


    return (args["file"], args["output"])


def get_text_id( text):
    """
    Returns the ID of the text, creates a new ID if it does not exists in the texts dictionary
    :param text:
    :return:
    """

    global id_counter, texts, links

    if text in texts:
        return texts[text]
    else:
        id_counter = id_counter + 1
        texts[text] = id_counter
        links[id_counter] = []
        return id_counter


def write_file( dir, id, text):
    """
    Write the XML file to the output
    :param dir:
    :param id:
    :param text:
    :return:
    """

    file = os.path.join( dir, f"{id}.xml");
    functions.write_file(file, text)



# Main part of the script
if __name__ == '__main__':
    (file, output) = read_arguments()

    functions.create_directory_if_not_exists(output)

    id_counter = 0
    with open(file) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            id1 = get_text_id(row[1])
            id2 = get_text_id(row[2])
            links[id1].append( id2)
            links[id2].append( id1)

    for text in texts.keys():
        write_file( output, texts[text], text)

    a = 0