# Class to read articles with the given subject from WikiData
import re
from WikiDataSparql import WDSparql
import os
import bz2
import pickle
import urllib.parse
import functions
from lxml import etree as ET

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
            print("One moment please, building index...")
            words = self.__make_wiki_index( index_file)
            file = open(pickle_file, "wb")
            words = pickle.dump(words, file)
            file.close()

        return words

    def __make_wiki_index(self, index_file):
        """
        Read the index file and create a dictionary with the words as keys and tuple (articleid, start, end)
        :param index_file:
        :return:
        """
        lines = self.__read_all_lines_from_bz2( index_file)
        lines_in_parts = [line.split(':', 2) for line in lines]
        pos = self.__read_from_to( lines_in_parts)

        words = {}
        # Loop through all lines
        for line in lines_in_parts:
            if len( line) == 3:  ## Only valid lines
                word = line[2].replace("&amp;", "&")
                if not word in words:
                    seekpos = line[0]
                    articleid = int( line[1])
                    words[word] = (pos[seekpos][0], pos[seekpos][1], articleid)

        return words




    def __read_from_to(self, lines):
        """
        returns a dictionary with a start position as a key and a tuple( start, end) as
        value. The key is a string, the tuple contains two integers. It uses the
        lines from the index as input and reads field 0 (the position)
        :param lines:
        :return:
        """
        current = ""
        positions = []
        for line in lines:
            if len(line) == 3  and  line[0] != current:
                current = line[0]
                positions.append( current)
        positions.append("0")

        pos = {}
        for i in range(0, len(positions) - 1):
            pos[positions[i]] = ( int(positions[i]), int(positions[i+1]))

        return pos


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
        Read al items from the given subject and return the ids and the urls in a tuple
        :return: (id, url, [properties])
        """

        query = f"""
            SELECT ?article ?item
            WHERE 
            {{
              VALUES ?subjects {{ {' '.join(self.subjects) } }} . 
              ?class wdt:P279* ?subjects .
              ?item ?relatie ?class. 
              ?article schema:about ?item.
              ?article schema:isPartOf <https://{self.language}.wikipedia.org/>
            }}                        
        """
        rows = self.wikidata.query( query, "read_all_items_" + self.uniqueid)
        articles = []

        # Read items from results
        for row in rows:
            article = row["article"]["value"]
            item = row["item"]["value"].replace('http://www.wikidata.org/entity/', 'wd:') # Just have the id
            articles.append( (item, article) )

        # all items and urls
        return articles


    def read_wikipedia_article(self, wikidata_id, name):
        """
        Read the xml for the wikipedia article
        Parts of the code come from: https://data-and-the-world.onrender.com/posts/read-wikipedia-dump/
        :param url: wikipedia url
        :return:
        """

        if not name in self.wikindex:
            print(f"Unknown article '{name}'")
        else:
            decomp = bz2.BZ2Decompressor()
            with open( self.dump_file, 'rb') as file:
                (start, end, articleid) = self.wikindex[name]
                file.seek( start)  # Go to right position
                read = file.read( end - start - 1 )
                page_xml = decomp.decompress( read).decode()
                return self.__get_article_from_xml(page_xml, articleid, wikidata_id)


    def url_to_name(self, url):
        """
        Translates a wikipedia url into a name
        :param url:
        :return:
        """

        parts = url.split("/")  # last part of url
        name = parts[len(parts)-1]
        name = name.replace("_", " ")
        name = urllib.parse.unquote( name)

        return name


    def __get_article_from_xml(self, xml, articleid, wikidata_id):
        """
        Read the article from the page xml
        :param xml:
        :param articleid:
        :param id: wikidataid
        :return:
        """

        doc = ET.fromstring( "<doc>" + xml + "</doc>")
        for page in doc.findall("page"):
            id = int(page.find("id").text)
            if( id == articleid):
                return self.__article_xml_to_text( page, wikidata_id)

        return "" # not found



    def __article_xml_to_text(self, page, wikidata_id):
        """
        Retrieves the text from the page element
        :param page:
        :return:
        """

        article = ET.Element("article")

        ET.SubElement( article, "id").text = wikidata_id
        ET.SubElement(article, "title").text = page.find("title").text
        ET.SubElement(article, "text").text = page.find("revision").find("text").text

        return functions.xml_as_string(article)




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

