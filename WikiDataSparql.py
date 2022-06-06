# Class to query data from WikiData.

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import os
import json
import time
import functions

class WDSparql:
    """
    Sparql queries for WikiData. Takes care of the limits:
        - One client (user agent + IP) is allowed 60 seconds of processing time each 60 seconds
        - One client is allowed 30 error queries per minute
    Therefore results are cached in a file
    """

    delayBetweenCallsInms = 2.1

    def __init__(self, cachedir, endpoint_url, debug=False):
        if not os.path.isdir( cachedir): # Create directory if not exists
            os.mkdir( cachedir)

        self.cache_dir = cachedir
        self.endpoint_url = endpoint_url
        self.debug = debug



    def query(self, sparql, name):
        """
        Call the query, if a file exists with the given name the cached data is returned
        :param sparql: the query
        :param name: chache name
        :return: object with the data
        """

        short = functions.hash_string(name)
        cache_file = os.path.join( self.cache_dir, f"{short}.json")
        if not self.debug and os.path.isfile( cache_file):
            results = functions.read_file( cache_file)
        else:
            results = self.__perform_query( sparql)
            functions.write_file( cache_file, results)

        return json.loads(results)["results"]["bindings"]



    def __perform_query(self, sparql):
        """
        Perform the query and return the resulting json
        :param sparql: the query
        :return: JSON string
        """

        headers = {
            "User-Agent": "Other",
            "content-type": "application/json"
        }

        parameters = {
            "format": "json",
            "query": sparql
        }


        r = requests.get(url=self.endpoint_url, params=parameters, headers = headers)
        time.sleep(WDSparql.delayBetweenCallsInms)  # Make sure we don't cross the limits

        return r.text




