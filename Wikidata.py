# Class to read articles with the given subject from WikiData
import re
from WikiDataSparql import WDSparql
import requests
import os
import bz2
import pickle

class Wikidata:
    max_number_of_ids_for_wbgetentities = 50  # Maximum number of IDs to be queried at once


    def __init__(self, wikidata_endpoint, subjects, language, dump_dir, debug=False):
        """
        :param wikidata_endpoint: Wikidata SPARQL endpoint
        :param subjects: subject for the articles
        """
        self.wikidata = WDSparql( "cache", wikidata_endpoint,debug=debug)
        self.subjects = subjects
        self.uniqueid = "-".join( subjects).replace(":", "_") + "-" + language
        self.debug = debug
        self.language = language
        (self.dump_file, self.index_file) =  self.__check_dump_dir( dump_dir, language)
        self.wikindex = self.__read_wiki_index( self.index_file)


    def __check_dump_dir(self, dump_dir, language):
        """
        Check if the dump directory contains the right files it should contain a index and dump file for the
        language.
        :param dump_dir:
        :param language:
        :return: (dump_file, index_file)
        """
        if os.path.isdir( dump_dir):
            files = os.listdir( dump_dir)

            dump_re = re.compile(language + "wiki-(\d{8})-pages-articles-multistream.xml.bz2")
            dump_files = list( filter( dump_re.match, files))

            if(len(dump_files) > 0):
                dump_file = dump_files[0]
                index_file = dump_file.replace( ".xml.bz2", "-index.txt.bz2") # To make sure we use the same date
                if index_file in files:
                    return( os.path.join( dump_dir, dump_file), os.path.join(dump_dir, index_file))

            print(f"Dump file does not contain the right files, use the multistream xml file for this language and the accompanying index file")


    def __read_wiki_index(self, index_file):
        """
        Read the index file and create a dictionary with the words as keys and tuple (start, end)
        It tries to load the data from a pickle file
        :param index_file:
        :return:
        """

        pickle_file = index_file.replace("txt.bz2", "pkl")
        if os.path.isfile( pickle_file):
            file = open(pickle_file, "rb")
            words = pickle.load(file)
            file.close()
        else:
            words = self.__make_wiki_index( index_file)
            file = open(pickle_file, "wb")
            words = pickle.dump(words, file)
            file.close()

        return words

    def __make_wiki_index(self, index_file):
        """
        Read the index file and create a dictionary with the words as keys and tuple (start, end)
        :param index_file:
        :return:
        """
        lines = self.__read_all_lines_from_bz2( index_file)
        lines_in_parts = [line.split(':') for line in lines]
        lines_in_parts += [0,0,"EOF"]  # The last word in the index, skip it for now
        words = {}
        # Loop through all lines
        for i in range(0, len(lines_in_parts) - 2):
            if len( lines_in_parts[i]) == 3:
                word = lines_in_parts[i][2]
                if not word in words:
                    words[word] = (lines_in_parts[i][0], 0)

        return words


    def __read_all_lines_from_bz2(self, filename):
        """
        Read all lines from a bz2 file
        :param filename:
        :return:
        """

        file = bz2.BZ2File(filename, "r")
        text = file.read().decode("utf-8")
        file.close()

        return text.split("\n")

    def read_all_items(self):
        """
        Read al items from the given subject and return the ids
        :return:
        """

        query = f"""
            SELECT ?article 
            WHERE 
            {{
              VALUES ?subjects {{ {' '.join(self.subjects) } }} . 
              ?class wdt:P279* ?subjects .
              ?item wdt:P31 ?class. 
              ?article schema:about ?item.
              ?article schema:isPartOf <https://{self.language}.wikipedia.org/>
            }}                        
        """
        items = self.wikidata.query( query, "read_all_items_" + self.uniqueid)
        articles = set()

        # Read items from results
        for item in items:
            article = item["article"]["value"]
            articles.add( article)

        # all sub classes
        return list( articles)



    @staticmethod
    def check_property(subjects):
        """
        Checks if a property looks like a list of valid wikidata properties
        :param subjects: The subject to be checked
        :return: "" if OK, a error message otherwise
        """

        for subject in subjects:
            if re.search("^wd:Q\d+$", subject) == None:
                return f"Invalid property, it must have the format wd:Q123"

        return ""

