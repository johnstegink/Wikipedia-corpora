# Class create links between files
import xml.etree.ElementPath

from lxml import etree as ET
import functions
import os

class Links:
    def __init__(self, files):
        """
        Create a sections object
        :param files: filenames to be processed
        """

        self.files = files



    def __read_info(self, filename):
        """
        Reads the title, id and a list of links from the filename
        :param filename:
        :return: (title, id, links)
        """

        xml = ET.parse(filename)
        title = xml.find("title").text
        id = xml.find("id").text

        linkElems = xml.getroot().iter("link")
        if linkElems is None:  # Always return a list
            links = []
        else:
            links = [ link.text for link in linkElems]

        return( title, id, links)


    def read_names_and_links(self):
        """
        Returns a dictionary with all titles and corresponding ids and a dictionary with all ids and sets with
        outgoing hyperlinks
        :return: (name_to_id, links_in_id)
        """

        name_to_id = {}
        links_in_id = {}
        for file in self.files:
            (title, id, links) = self.__read_info( file)
            if not "_" in id:  # Only main entries
                name_to_id[title] = id

            links_in_id[id] = set(links)

        return (name_to_id, links_in_id)