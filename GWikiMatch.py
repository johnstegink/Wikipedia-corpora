# Class to process GWikiMatch files obtained from https://github.com/google-research/google-research/tree/master/gwikimatch
import functions
from Wikidata import Wikidata
from WikiDataSparql import WDSparql
import os

class GWikiMatch:

    def __init__(self, dir, wikidata_endpoint, debug):
        """
        Constructor
        :param dir: directory with gwikimatch files
        :param wikidata_endpoint:
        :param debug:
        """
        self.wikidata_endpoint = wikidata_endpoint
        self.debug = debug
        self.info = self.__read_data( dir)



    def __read_data(self, dir):
        chache_file = os.path.join(dir, "cache.txt")
        self.info = []

        if not os.path.exists( chache_file):
            self.__create_cache_file(chache_file, dir)

        for line in functions.read_file(chache_file).split("\n"):
            fields = line.split("\t")
            if len(fields) == 3:
                positive = fields[0] == "1"
                self.info.append((fields[1], fields[2], positive))



    def __create_cache_file(self, chache_file, dir):
        """
        Create a chache file with the url's translated to wikidata URLs
        :param chache_file:
        :return:
        """

        print( "Creating GWikiMatch cache file...")
        data = self.__process_files(dir)
        translation = self.__read_ids_of_articles(data)
        lines = []
        for datum in data:
            if datum[0] in translation and datum[1] in translation:
                lines.append(f"{translation[datum[0]]}\t{translation[datum[1]]}\t{'1' if datum[2] else '0' }")

        functions.write_file(chache_file, "\n".join(lines))
        print("Done.")



    def __process_file(self, file):
        """
        Process the file
        :param file:
        :return: a list of tuples in the form (from, to, isPositive)
        """
        info = []
        for line in functions.read_file(file).split("\n"):
            fields = line.split("\t")
            if len(fields) == 3:
                positive = fields[0] == "1"
                info.append( (fields[1], fields[2], positive))

        return info


    def __process_files(self, dir):
        """
        Processes all files in the directory
        :param dir:
        :return: a list of tuples in the form (from, to, isPositive)
        """
        lines = []
        for file in functions.read_all_files_from_directory(dir, "tsv"):
            lines = lines + self.__process_file( file)

        return lines



    def __get_all_articles(self, info):
        """
        Get a set of unique articles from the info
        :return: list
        """

        articles = set()
        for line in info:
            articles.add( line[0])
            articles.add( line[1])

        return articles


    def __read_ids_of_articles(self, info):
        """
        Read all ids of the all articles
        :return: dictionary with the url as key and the Wikidata a value
        """

        translation = {}
        articles = list(self.__get_all_articles(info))
        articles.sort()
        wikidata = WDSparql( "cache", self.wikidata_endpoint, self.debug)

        for chunk in functions.create_chunks_of_list( articles, 50):
            for row in self.__translate_to_ids(chunk, wikidata):
                translation[row[0]] = row[1]

        return translation



    def __translate_to_ids(self, urls, wikidata):
        """
        Performs a SPARQL query to translate the urls to WikiData IDs
        :param urls:
        :return: list of tuples [(url,id)]
        """
        wikidataurls = ["<" + url.replace("http://", "https://") + ">" for url in urls]
        query = f"""
        SELECT ?item ?urls WHERE {{
          VALUES ?urls {{
            {" ".join( wikidataurls)}
          }}
          
          ?urls schema:about ?item
        }}
        """
        rows = wikidata.query( query, "translate_" + query)

        translation = []

        # Read items from results
        for row in rows:
            id = row["item"]["value"].replace('http://www.wikidata.org/entity/', '') # Just the ID
            url = row["urls"]["value"].replace('https://', 'http://') # translate into http
            translation.append( (url, id))

        return translation

