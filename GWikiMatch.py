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
        """
        Read data from the cache file, if it not exists it will be created
        :param dir: directory with GWikiMatch data
        :return: list of tuples with WikiDataIds (source, destination, class)
        """
        chache_file = os.path.join(dir, "cache.txt")
        self.info = []

        if not os.path.exists( chache_file):
            self.__create_cache_file(chache_file, dir)

        info = []
        for line in functions.read_file(chache_file).split("\n"):
            fields = line.split("\t")
            if len(fields) == 3:
                info.append((fields[0], fields[1], fields[2]))

        return info


    def __create_cache_file(self, cache_file, dir):
        """
        Create a chache file with the url's translated to wikidata URLs
        :param cache_file:
        :return:
        """

        print( "Creating GWikiMatch cache file...")
        data = self.__process_files(dir)
        translation = self.__read_ids_of_articles(data)
        lines = []
        for datum in data:
            if datum[0] in translation and datum[1] in translation:
                lines.append(f"{translation[datum[0]]}\t{translation[datum[1]]}\t{datum[2]}")

        functions.write_file(cache_file, "\n".join(lines))
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
                info.append( (fields[1], fields[2], fields[0]))

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


    def __get_urls_of_ids(self, ids, language, wikidata):
        """
        Performs a SPARQL query to translate the ids to corresponding wikipedia urls
        :param  ids:
        :return: list of tuples [(url,id)]
        """

        wikidataids = ["wd:" + id for id in ids]
        query = f"""
        SELECT ?article ?items WHERE {{
          VALUES ?items {{
            {" ".join(wikidataids)}
          }}

        ?article schema:about ?items.
        ?article schema:isPartOf <https://{language}.wikipedia.org/>
        }}
        """
        rows = wikidata.query(query, "translate_" + query)
        translation = []

        # Read items from results
        for row in rows:
            id = row["items"]["value"].replace('http://www.wikidata.org/entity/', '') # Just the ID
            url = row["article"]["value"]
            translation.append( (id,url))

        return translation



    def append_to_filtered_file(self, file, ids):
        """
        Creates a file with all relations from the given ids
        :param file: the file to be created
        :param ids: set with ids to be used for filtered
        :return: nothing
        """

        lines = []
        for info in self.info:
            if info[0] in ids and info[1] in ids:
                lines.append(f"{info[0]}\t{info[1]}\t{info[2]}")

        functions.append_file(file, "\n".join(lines))




    def get_all_articles_with_url(self, language):
        """
        returns a list of articles with the corresponding url in the given language
        :param language:
        :return:  [(id, url)]
        """

        articles = list( self.__get_all_articles( self.info))
        articles.sort()
        wikidata = WDSparql( "cache", self.wikidata_endpoint, self.debug)

        with_url = []
        for chunk in functions.create_chunks_of_list( articles, 500):
            for row in self.__get_urls_of_ids(chunk, language, wikidata):
                with_url.append( row)

        return with_url


    def get_links_of_article(self, id):
        """
        Get all links belonging to an article
        :param id:
        :return: [(id, class)] where class = 0, 1 or 2
        """

        links = []
        for record in self.info:
            if record[0] == id:
                links.append( (record[1], record[2]) )
            elif record[1] == id:
                links.append( (record[0], record[2]) )

        return links