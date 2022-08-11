import hashlib
import os
import shutil
from pathlib import Path
from lxml import etree as ET



def hash_string(to_be_hashed):
    """
    Creates a hash string of the string, only for uniqueness
    """

    hash_object = hashlib.sha1(to_be_hashed.encode())
    return hash_object.hexdigest()


def create_directory_if_not_exists(dir_name):
    """
    Creates a directory if it doesn't exist
    :param dir_name:
    :return:
    """

    os.makedirs( dir_name, exist_ok=True)
    # delete all files
    # for file in read_all_files_from_directory( dir_name, "*"):
        # os.remove(file)


def remove_redirectory_recursivly( dir_name):
    shutil.rmtree( dir_name)


def read_all_files_from_directory(dir_name, extension):
    """
    Read all files from a directory, recursively
    :param dir_name:
    :param extension
    :return:
    """
    return list( Path(dir_name).rglob("*." + extension))


def read_file(filename):
    """
    Read entire text of file
    :param filename: path to the file
    :return: contents of file
    """

    file = open( filename, mode="r", encoding="utf-8")
    contents = file.read()
    file.close()

    return contents


def write_file(filename, contents):
    """
    Write text contents to a file
    :param filename: path to the file
    :param contents: textcontents
    :return: -
    """

    file = open( filename, mode="w", encoding="utf-8")
    file.write( contents)
    file.close()

def append_file(filename, contents):
    """
    Append text contents to a file
    :param filename: path to the file
    :param contents: textcontents
    :return: -
    """

    file = open( filename, mode="a", encoding="utf-8")
    file.write( contents)
    file.close()




def xml_as_string(element):
    """
    Create xml string of the element
    :param element:
    :return:
    """
    return ET.tostring(element, encoding='unicode', method='xml', pretty_print=True)

def create_chunks_of_list(theList, chunk_size):
    """
    Splits a list into lists with chunks
    :param theList:
    "param chunk_size
    :return:
    """

    return [theList[i:i + chunk_size] for i in range(0, len(theList), chunk_size)]

def write_corpus_info(corpusdir, name, language_code):
    """
    Write the corpus info
    :param corpusdir:
    :param name:
    :param language_code:
    :return:
    """
    root = ET.fromstring("<corpus></corpus>")
    ET.SubElement( root, "name").text = name
    ET.SubElement( root, "language_code").text = language_code

    write_file( os.path.join( corpusdir, "corpus.info"), xml_as_string( root))


def read_corpus_info(corpusdir):
    """
    Reads the corpus info
    :param corpusdir:
    :return: (name, language_code)
    """

    doc = ET.parse(Path.joinpath( corpusdir, "corpus.info"))
    corpus = doc.getroot()
    name = corpus.find("name").text
    language_code = corpus.find("language_code").text

    return (name, language_code)