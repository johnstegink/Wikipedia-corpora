# Class to read articles with the given subject from WikiData
import re
from WikiDataSparql import WDSparql
import requests


class Wikidata:
    max_number_of_ids_for_wbgetentities = 50  # Maximum number of IDs to be queried at once


    def __init__(self, wikidata_endpoint, subjects, language, debug=False):
        """
        :param wikidata_endpoint: Wikidata SPARQL endpoint
        :param subjects: subject for the articles
        """
        self.wikidata = WDSparql( "cache", wikidata_endpoint,debug=debug)
        self.subjects = subjects
        self.uniqueid = "-".join( subjects)
        self.debug = debug
        self.language = language


    def __read_all_classes(self):
        """
        Read al items from the given subject and return the ids
        :return:
        """

        query = f"""
            SELECT ?class WITH {{
                SELECT ?class {{
                  VALUES ?subjects {{ {' '.join(self.subjects) } }} . 
                  ?class wdt:P279* ?subjects .
                }}
              }} AS %items WHERE {{ 
                INCLUDE %items .
            }}
                        """
        items = self.wikidata.query( query, "read_all_classes_" + self.uniqueid)
        classes = set()

        # Read items from results
        for item in items:
            classes.add( item["class"]["value"])

        # all sub classes
        return list( classes)


    def read_all_items(self):
        """
        Read al items from the given subject and return the ids
        :return:
        """
        classes = self.__read_all_classes()
        query = f"""
			SELECT ?item 
			WHERE
            {{
			   VALUES ?classes {{ {' '.join(classes)} }} 
			   ?item wdt:P31 ?classes  
			}}                        
		"""
        items = self.wikidata.query( query, "read_all_items_" + self.uniqueid)
        itms = set()

        # Read items from results
        for item in items:
            itms.add( item["item"]["value"])

        # all sub classes
        return list( itms)


    def read_urls_from_ids(self, ids):
        """
        Reads all url's from the given IDs for the given language
        :param ids:
        :return: list of urls
        """

        urls = []
        number_of_ids = len(ids)
        number_asked = 0
        while number_asked < number_of_ids:
            # divide the ids in parts because there is a maximum to the number of query IDs
            query_ids = ids[number_asked:(number_asked + Wikidata.max_number_of_ids_for_wbgetentities)]
            number_asked += Wikidata.max_number_of_ids_for_wbgetentities

            urls += self.get_url_from_ids(query_ids)

        return urls
        #     if entity:
        #         sitelinks = entity.get('sitelinks')
        #         if sitelinks:
        #             if lang:
        #                 # filter only the specified language
        #                 sitelink = sitelinks.get(f'{lang}wiki')
        #                 if sitelink:
        #                     wiki_url = sitelink.get('url')
        #                     if wiki_url:
        #                         return requests.utils.unquote(wiki_url)
        #             else:
        #                 # return all of the urls
        #                 wiki_urls = {}
        #                 for key, sitelink in sitelinks.items():
        #                     wiki_url = sitelink.get('url')
        #                     if wiki_url:
        #                         wiki_urls[key] = requests.utils.unquote(wiki_url)
        #                 return wiki_urls
        return None

    def get_url_from_ids(self, ids):
        """
        get the url's for the specific language for the ids
        :param ids:
        :return: ids
        """

        urls = []
        lang_wiki = f'{self.language}wiki'

        api_url = (
            'https://www.wikidata.org/w/api.php'
            '?action=wbgetentities'
            '&props=sitelinks/urls'
            f'&languages={self.language}'
            f'&ids={"|".join(ids)}'
            '&format=json')
        json_response = requests.get(api_url).json()
        entities = json_response.get('entities')
        for entity in entities:
            if "sitelinks" in entity and lang_wiki in entity["sitelinks"] and "url" in entity["sitelinks"][lang_wiki]:
                wiki_url = requests.utils.unquote(entity["sitelinks"][lang_wiki]["url"])
                urls.append(wiki_url)

        return urls

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

