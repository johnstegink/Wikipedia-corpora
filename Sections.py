# Class to split Wikipedia article in sections
from lxml import etree as ET
import functions
import os
import re
import wikitextparser as wtp

class Sections:
    def __init__(self, contents, name, output_dir ):
        """
        Create a sections object
        :param contents: Xml contents
        :param name: Name of the file, without extension
        :param output_dir:
        """

        self.xml = ET.fromstring( contents)
        self.contents = contents
        self.name = name
        self.output_dir = output_dir


    def __get_tekst(self, part):
        """
        Get the plain text and puts it in the text element
        :param part:
        :return:
        """
        text = part.plain_text().replace("==", " ")

        elem = ET.Element("text")
        elem.text = text

        return elem


    def __get_links(self, part):
        """
        Returns a list of links to other articles
        :param part:
        :return:
        """

        linksElem = ET.Element("links")
        for link in part.wikilinks:
            linkElem = ET.Element("link")
            linkElem.text = link.target
            linksElem.append( linkElem)

        return linksElem


    def __save_xml(self, part, suffix):
        """
        Create the xml and save it a file with the given suffix, can be empty
        :param part:
        :param suffix:
        :return:
        """
        doc = ET.Element("doc")
        doc.append( self.__get_tekst( part))
        doc.append( self.__get_links( part))

        filename = os.path.join( self.output_dir, f"{self.name}{suffix}.xml")
        functions.write_file(filename, functions.xml_as_string(doc))



    def create_sections(self):
        """
        Create sections into the output dir
        :param output_dir:
        :return:
        """

        text = self.xml.find("text").text
        page = wtp.parse( text)

        self.__save_xml(page,"")

        id_counter = 1
        for section in page.sections:
            self.__save_xml(section, str(id_counter))
            id_counter += 1

